import logging
import re
from ._parser import HtmlParser
from typing import List, Optional, Tuple
from parsel import Selector
from pyutils.strings import find_date, remove_parenthesis, whitespaces_clean, remove_roman
from rscraping.data.constants import (
    GENDER_FEMALE,
    GENDER_MALE,
    PARTICIPANT_CATEGORY_ABSOLUT,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from rscraping.data.functions import is_play_off
from rscraping.data.models import Datasource, Participant, Race
from rscraping.data.normalization.clubs import normalize_club_name
from rscraping.data.normalization.times import normalize_lap_time
from rscraping.data.normalization.races import normalize_race_name

logger = logging.getLogger(__name__)


class ACTHtmlParser(HtmlParser):
    DATASOURCE = Datasource.ACT

    def parse_race(self, selector: Selector, race_id: str, is_female: bool, **_) -> Optional[Race]:
        name = self.get_name(selector)
        logger.info(f"{self.DATASOURCE}: found race {name}")

        # parse name, edition, and date from the page title (<edition> <race_name> (<date>))
        edition = self.get_edition(name)
        t_date = find_date(name)
        gender = GENDER_FEMALE if is_female else GENDER_MALE

        if not t_date:
            raise ValueError(f"{self.DATASOURCE}: no date found for {name=}")

        name = self._normalize_race_name(name, is_female=is_female)
        name, edition = self._hardcoded_name_edition(name, is_female=is_female, year=t_date.year, edition=edition)
        if not name:
            logger.error(f"{self.DATASOURCE}: no race found for {race_id=}")
            return None
        logger.info(f"{self.DATASOURCE}: race normalized to {name=}")

        participants = self.get_participants(selector)

        race = Race(
            name=name,
            normalized_name=normalize_race_name(name, is_female),
            date=t_date.strftime("%d/%m/%Y"),
            type=self.get_type(participants),
            edition=edition,
            day=self.get_day(selector),
            modality=RACE_TRAINERA,
            league=self.get_league(selector, is_female),
            town=self.get_town(selector),
            organizer=self.get_organizer(selector),
            race_id=race_id,
            url=None,
            gender=gender,
            datasource=self.DATASOURCE.value,
            cancelled=self.is_cancelled(selector),
            race_laps=self.get_race_laps(selector),
            race_lanes=self.get_race_lanes(participants),
            participants=[],
        )

        for row in participants:
            race.participants.append(
                Participant(
                    gender=gender,
                    category=PARTICIPANT_CATEGORY_ABSOLUT,
                    club_name=self.get_club_name(row),
                    lane=self.get_lane(row),
                    series=self.get_series(selector, row),
                    laps=self.get_laps(row),
                    distance=self.get_distance(is_female),
                    participant=normalize_club_name(self.get_club_name(row)),
                    race=race,
                )
            )

        return race

    def parse_race_ids(self, selector: Selector, **_) -> List[str]:
        urls = selector.xpath('//*[@id="col-a"]/div/section/div[5]/table/tbody/tr[*]/td[*]/a/@href').getall()
        return [url_parts[-1] for url_parts in (url.split("r=") for url in urls)]

    def parse_lineup(self, **_):
        raise NotImplementedError

    ####################################################
    #                     GETTERS                      #
    ####################################################

    def get_name(self, selector: Selector) -> str:
        return whitespaces_clean(selector.xpath('//*[@id="col-a"]/div/section/div[1]/h3/text()').get("")).upper()

    def get_day(self, selector: Selector) -> int:
        name = self.get_name(selector)
        if is_play_off(name):
            return 1 if "1" in name else 2

        matches = re.findall(r"\(?(\dJ|J\d)\)?", name)
        return int(re.findall(r"\d+", matches[0])[0].strip()) if matches else 1

    def get_type(self, participants: List[Selector]) -> str:
        lanes = list(self.get_lane(p) for p in participants)
        return RACE_TIME_TRIAL if all(int(lane) == int(lanes[0]) for lane in lanes) else RACE_CONVENTIONAL

    def get_league(self, selector: Selector, is_female: bool) -> Optional[str]:
        return "ACT" if is_play_off(self.get_name(selector)) else "LIGA EUSKOTREN" if is_female else "EUSKO LABEL LIGA"

    def get_town(self, selector: Selector) -> str:
        return whitespaces_clean(
            selector.xpath('//*[@id="col-a"]/div/section/div[2]/table/tbody/tr/td[2]/text()').get("")
        ).upper()

    def get_organizer(self, selector: Selector) -> Optional[str]:
        organizer = whitespaces_clean(
            selector.xpath('//*[@id="col-a"]/div/section/div[2]/table/tbody/tr/td[1]/text()').get("")
        ).upper()
        return organizer if organizer else None

    def get_race_lanes(self, participants: List[Selector]) -> int:
        if self.get_type(participants) == RACE_TIME_TRIAL:
            return 1
        lanes = list(self.get_lane(p) for p in participants)
        return max(int(lane) for lane in lanes)

    def get_race_laps(self, selector: Selector) -> int:
        cia = selector.xpath('//*[@id="col-a"]/div/section/div[3]/div[2]/div/table/thead/tr/th[*]/text()').getall()
        return len(cia) + 1

    def is_cancelled(self, selector: Selector) -> bool:
        # race_id=1301303104|1301302999
        # try to find the "No puntuable" text in the header
        return selector.xpath('//*[@id="col-a"]/div/section/div[1]/p/span/text()').get("").upper() == "NO PUNTUABLE"

    def get_participants(self, selector: Selector) -> List[Selector]:
        rows = selector.xpath('//*[@id="col-a"]/div/section/div[*]/div[2]/div/table/tbody/tr[*]').getall()
        return [Selector(text=t) for t in rows]

    def get_lane(self, participant: Selector) -> int:
        lane = participant.xpath("//*/td[1]/text()").get()
        return int(lane) if lane else 0

    def get_club_name(self, participant: Selector) -> str:
        name = participant.xpath("//*/td[2]/text()").get()
        return whitespaces_clean(name).upper() if name else ""

    def get_distance(self, is_female: bool) -> int:
        return 2778 if is_female else 5556

    def get_laps(self, participant: Selector) -> List[str]:
        laps = participant.xpath("//*/td/text()").getall()[2:-1]
        return [t.strftime("%M:%S.%f") for t in [normalize_lap_time(e) for e in laps if e] if t is not None]

    def get_series(self, selector: Selector, participant: Selector) -> int:
        series = 1
        for table in selector.xpath('//*[@id="col-a"]/div/section/div[*]/div[2]/div/table/tbody').getall():
            for p in Selector(table).xpath("//*/tr[*]").getall():
                if p == participant:
                    return series
            series += 1
        return 0

    ####################################################
    #                  NORMALIZATION                   #
    ####################################################
    @staticmethod
    def _normalize_race_name(name: str, is_female: bool = False) -> str:
        # remove edition and parenthesis
        name = remove_roman(remove_parenthesis(whitespaces_clean(name)))

        # remove day
        name = re.sub(r"\(?(\dJ|J\d)\)?", "", name)

        # remove waste
        if "-" in name:
            part1, part2 = whitespaces_clean(name.split("-")[0]), whitespaces_clean(name.split("-")[1])

            if "OMENALDIA" in part2:  # tributes
                name = part1
            elif "BILBAO" in part2:
                name = "BANDERA DE BILBAO" if "BANDERA DE BILBAO" == part2 else "GRAN PREMIO VILLA DE BILBAO"
            elif any(w in part1 for w in ["BANDERA", "BANDEIRA", "IKURRIÑA"]):
                name = part1

        return normalize_race_name(name, is_female)

    @staticmethod
    def _hardcoded_name_edition(name: str, is_female: bool, year: int, edition: int) -> Tuple[str, int]:
        if "ASTILLERO" in name:
            name, edition = "BANDERA AYUNTAMIENTO DE ASTILLERO", (year - 1970)

        if "ORIOKO" in name:
            name = "ORIOKO ESTROPADAK"

        if "CORREO IKURRIÑA" in name:
            name, edition = "EL CORREO IKURRIÑA", (year - 1986)

        if "EL CORTE" in name:
            name, edition = "GRAN PREMIO EL CORTE INGLÉS", (year - 1970)

        if is_play_off(name):
            name, edition = ("PLAY-OFF ACT (FEMENINO)", (year - 2017)) if is_female else ("PLAY-OFF ACT", (year - 2002))

        return name, edition
