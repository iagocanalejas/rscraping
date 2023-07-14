import logging
import re
from pypdf import PdfReader
import requests

from ._client import Client
from io import BytesIO
from datetime import date, datetime
from typing import List, Optional, Tuple
from parsel import Selector
from pyutils.strings.cleanup import remove_parenthesis, remove_roman, whitespaces_clean
from data.constants import (
    GENDER_FEMALE,
    GENDER_MALE,
    HTTP_HEADERS,
    PARTICIPANT_CATEGORY_ABSOLUT,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from data.functions import is_play_off
from data.normalization.clubs import normalize_club_name
from data.normalization.times import normalize_lap_time
from data.normalization.trophies import normalize_trophy_name
from data.models import Datasource, Lineup, Participant, Race
from parsers.pdf.lineup import LGTLineupPdfParser

logger = logging.getLogger(__name__)


class LGTClient(Client, source=Datasource.LGT):
    DATASOURCE = Datasource.LGT

    _results_selector: Selector

    @staticmethod
    def get_url(race_id: str, **_) -> str:
        return f"https://www.ligalgt.com/principal/regata/{race_id}"

    @staticmethod
    def get_lineup_url(race_id: str, **_) -> str:
        return f"https://www.ligalgt.com/pdf/alinacion.php?regata_id={race_id}"

    @staticmethod
    def get_results_selector(race_id: str) -> Selector:
        url = "https://www.ligalgt.com/ajax/principal/ver_resultados.php"
        data = {"liga_id": 1, "regata_id": race_id}
        return Selector(requests.post(url=url, headers=HTTP_HEADERS, data=data).text)

    def get_race_by_id(self, race_id: str, **_) -> Optional[Race]:
        url = self.get_url(race_id)
        self._selector = Selector(requests.get(url=url, headers=HTTP_HEADERS).text)
        self._results_selector = self.get_results_selector(race_id)

        name = self.get_name()
        logger.info(f"{self.DATASOURCE}: found race {name}")

        t_date = self.get_date()
        is_female = any(e in name for e in ["FEMENINA", "FEMININA"])
        edition = self.get_edition(name)
        gender = GENDER_FEMALE if is_female else GENDER_MALE

        name = self._normalize_race_name(name, is_female=is_female)
        name, edition = self._hardcoded_playoff_edition(name, year=t_date.year, edition=edition)
        if not name:
            logger.error(f"{self.DATASOURCE}: no race found for {race_id=}")
            return None
        logger.info(f"{self.DATASOURCE}: race normalized to {name=}")

        participants = self.get_participants()

        race = Race(
            name=name,
            trophy_name=normalize_trophy_name(name, is_female),
            date=t_date.strftime("%d/%m/%Y"),
            type=self.get_type(participants),
            edition=edition,
            day=self.get_day(),
            modality=RACE_TRAINERA,
            league=self.get_league(),
            town=self.get_town(),
            organizer=self.get_organizer(),
            race_id=race_id,
            url=url,
            datasource=self.DATASOURCE.value,
            cancelled=self.is_cancelled(participants),
            race_laps=self.get_race_laps(),
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
                    series=self.get_series(row),
                    laps=self.get_laps(row),
                    distance=self.get_distance(),
                    participant=normalize_club_name(self.get_club_name(row)),
                    race=race,
                )
            )

        return race

    def get_lineup_by_race_id(self, race_id: str, **_) -> List[Lineup]:
        url = self.get_lineup_url(race_id)
        raw_pdf = requests.get(url=url, headers=HTTP_HEADERS).content

        parsed_items: List[Lineup] = []
        parser = LGTLineupPdfParser(source=self.DATASOURCE)

        with BytesIO(raw_pdf) as pdf:
            for page in PdfReader(pdf).pages:
                items = parser.parse_page(page=page)
                if items:
                    parsed_items.append(items)

        return parsed_items

    ####################################################
    #                     GETTERS                      #
    ####################################################

    def get_name(self) -> str:
        return whitespaces_clean(
            self._selector.xpath('//*[@id="regata"]/div/div/div[3]/div[2]/h1/text()').get("")
        ).upper()

    def get_date(self) -> date:
        value = whitespaces_clean(self._selector.xpath('//*[@id="regata"]/div/div/div[3]/div[2]/p[2]/text()').get(""))
        return datetime.strptime(value, "%d/%m/%Y").date()

    def get_day(self) -> int:
        name = self.get_name()
        if "XORNADA" in name:
            day = int(re.findall(r" \d+", name)[0].strip())
            return day
        if is_play_off(name):  # exception case
            if "1" in name:
                return 1
            if "2" in name:
                return 2
            return 2 if self.get_date().isoweekday() == 7 else 1  # 2 for sunday
        return 1

    def get_type(self, participants: List[Selector]) -> str:
        lanes = list(self.get_lane(p) for p in participants)
        return RACE_TIME_TRIAL if all(int(lane) == int(lanes[0]) for lane in lanes) else RACE_CONVENTIONAL

    def get_league(self) -> Optional[str]:
        if is_play_off(self.get_name()):
            return "LGT"
        return whitespaces_clean(
            self._selector.xpath('//*[@id="regata"]/div/div/div[3]/div[2]/p[3]/span/text()').get("")
        )

    def get_town(self) -> str:
        value = self._selector.xpath('//*[@id="regata"]/div/div/div[3]/div[2]/p[1]/text()').get("")
        return whitespaces_clean(value).upper().replace("PORTO DE ", "")

    def get_organizer(self) -> Optional[str]:
        organizer = self._selector.xpath('//*[@id="regata"]/div/div/div[3]/div[1]/text()').get("")
        organizer = whitespaces_clean(organizer).upper().replace("ORGANIZA:", "").strip() if organizer else None
        return normalize_club_name(organizer) if organizer else None

    def get_race_lanes(self, participants: List[Selector]) -> int:
        if self.get_type(participants) == RACE_TIME_TRIAL:
            return 1
        lanes = list(self.get_lane(p) for p in participants)
        return max(int(lane) for lane in lanes)

    def get_race_laps(self) -> int:
        return len(self._results_selector.xpath('//*[@id="tabla-tempos"]/tr[1]/th').getall()) - 2

    def is_cancelled(self, participants: List[Selector]) -> bool:
        # race_id=114
        # assume no final time is set for cancelled races (as in the example)
        times = [p.xpath("//*/td/text()").getall()[-1] for p in participants]
        return len([x for x in times if x == "-"]) > len(times) / 3

    def get_participants(self) -> List[Selector]:
        def is_valid(row: Selector) -> bool:
            return len(row.xpath("//*/td").getall()) > 1 and row.xpath("//*/td[2]/text()").get("") != "LIBRE"

        return [
            Selector(p)
            for p in self._results_selector.xpath('//*[@id="tabla-tempos"]/tr').getall()[1:]
            if is_valid(Selector(p))
        ]

    def get_lane(self, participant: Selector) -> int:
        lane = participant.xpath("//*/td[1]/text()").get()
        return int(lane) if lane else 0

    def get_club_name(self, participant: Selector) -> str:
        name = participant.xpath("//*/td[2]/text()").get()
        return whitespaces_clean(name).upper() if name else ""

    def get_distance(self) -> int:
        return 5556

    def get_laps(self, participant: Selector) -> List[str]:
        laps = participant.xpath("//*/td/text()").getall()[2:]
        return [t.strftime("%M:%S.%f") for t in [normalize_lap_time(e) for e in laps if e] if t is not None]

    def get_series(self, participant: Selector) -> int:
        series = 1
        rows = [Selector(p) for p in self._results_selector.xpath('//*[@id="tabla-tempos"]/tbody/tr[2]').getall()[1:]]
        for row in rows:
            if row == participant:
                return series
            if len(row.xpath("//*/td[*]").getall()) == 1:
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
        name = re.sub(r"(XORNADA )\d+|\d+( XORNADA)", "", name)

        # remove waste
        if name == "EREWEWEWERW" or name == "REGATA" or "?" in name:  # wtf
            return ""

        if "TERESA HERRERA" in name:  # lgt never saves the final
            return "TROFEO TERESA HERRERA (CLASIFICATORIA)"

        if "PLAY" in name:
            return "PLAY-OFF LGT"

        name = normalize_trophy_name(name, is_female)
        # remove gender
        for g in ["FEMENINA", "FEMININA"]:
            name = name.replace(g, "")

        return whitespaces_clean(name)

    @staticmethod
    def _hardcoded_playoff_edition(name: str, year: int, edition: int) -> Tuple[str, int]:
        if is_play_off(name):
            return name, (year - 2011)
        return name, edition
