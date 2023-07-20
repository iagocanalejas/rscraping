from datetime import date, datetime
import logging
import re
from ._parser import HtmlParser
from typing import List, Optional, Tuple
from parsel import Selector
from pyutils.strings import remove_parenthesis, whitespaces_clean, remove_roman
from data.constants import (
    GENDER_FEMALE,
    GENDER_MALE,
    PARTICIPANT_CATEGORY_ABSOLUT,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from data.functions import is_play_off
from data.models import Datasource, Lineup, Participant, Race
from data.normalization.clubs import normalize_club_name
from data.normalization.times import normalize_lap_time
from data.normalization.trophies import normalize_trophy_name

logger = logging.getLogger(__name__)


class ARCHtmlParser(HtmlParser):
    DATASOURCE = Datasource.ARC

    def parse_race(self, selector: Selector, race_id: str, is_female: bool, **_) -> Optional[Race]:
        name = self.get_name(selector)
        logger.info(f"{self.DATASOURCE}: found race {name}")

        gender = GENDER_FEMALE if is_female else GENDER_MALE

        name = self._normalize_race_name(name, is_female=is_female)
        if not name:
            logger.error(f"{self.DATASOURCE}: no race found for {race_id=}")
            return None
        logger.info(f"{self.DATASOURCE}: race normalized to {name=}")

        participants = self.get_participants(selector)

        race = Race(
            name=name,
            trophy_name=normalize_trophy_name(name, is_female),
            date=self.get_date(selector).strftime("%d/%m/%Y"),
            type=self.get_type(participants),
            edition=self.get_edition(name),
            day=self.get_day(selector),
            modality=RACE_TRAINERA,
            league=self.get_league(selector, is_female),
            town=self.get_town(selector),
            organizer=None,
            race_id=race_id,
            url=None,
            datasource=self.DATASOURCE.value,
            cancelled=self.is_cancelled(selector),
            race_laps=self.get_race_laps(selector),
            race_lanes=self.get_race_lanes(selector),
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

    def parse_lineup(self, selector: Selector, **_) -> Lineup:
        race = selector.xpath('//*[@id="main"]/div[2]/div[1]/h2/a/text()').get("")
        club = selector.xpath('//*[@id="main"]/div[2]/div[2]/div[1]/div[2]/div/h2/a/text()').get("")

        body = Selector(selector.xpath('//*[@id="regatas_hojas_impresion"]/table/tbody').get(""))
        coach = body.xpath("//*/tr[7]/td[2]/div/p/text()").get("")
        delegate = body.xpath("//*/tr[7]/td[1]/div/p/text()").get("")
        coxswain = body.xpath("//*/tr[13]/td[4]/div/div/p/a/text()").get("")
        bow = body.xpath("//*/tr[2]/td/div/div/p/a/text()").get("")

        starboard = [
            body.xpath("//*/tr[12]/td[5]/div/p/a/text()").get(""),
            body.xpath("//*/tr[11]/td[5]/div/p/a/text()").get(""),
            body.xpath("//*/tr[10]/td[5]/div/p/a/text()").get(""),
            body.xpath("//*/tr[9]/td[4]/div/p/a/text()").get(""),
            body.xpath("//*/tr[8]/td[5]/div/p/a/text()").get(""),
            body.xpath("//*/tr[7]/td[5]/div/p/a/text()").get(""),
        ]

        larboard = [
            body.xpath("//*/tr[12]/td[4]/div/p/a/text()").get(""),
            body.xpath("//*/tr[11]/td[4]/div/p/a/text()").get(""),
            body.xpath("//*/tr[10]/td[4]/div/p/a/text()").get(""),
            body.xpath("//*/tr[9]/td[3]/div/p/a/text()").get(""),
            body.xpath("//*/tr[8]/td[4]/div/p/a/text()").get(""),
            body.xpath("//*/tr[7]/td[4]/div/p/a/text()").get(""),
        ]

        substitute = [
            body.xpath("//*/tr[10]/td[1]/div/p/a/text()").get(""),
            body.xpath("//*/tr[10]/td[2]/div/p/a/text()").get(""),
            body.xpath("//*/tr[11]/td[1]/div/p/a/text()").get(""),
            body.xpath("//*/tr[11]/td[2]/div/p/a/text()").get(""),
            body.xpath("//*/tr[12]/td[1]/div/p/a/text()").get(""),
            body.xpath("//*/tr[12]/td[2]/div/p/a/text()").get(""),
            body.xpath("//*/tr[13]/td[1]/div/p/a/text()").get(""),
            body.xpath("//*/tr[13]/td[2]/div/p/a/text()").get(""),
        ]

        return Lineup(
            race=whitespaces_clean(race.upper()),
            club=whitespaces_clean(club.upper()),
            coach=whitespaces_clean(coach.upper()),
            delegate=whitespaces_clean(delegate.upper()),
            coxswain=whitespaces_clean(coxswain.upper()),
            starboard=[whitespaces_clean(s).upper() for s in starboard if s],
            larboard=[whitespaces_clean(s).upper() for s in larboard if s],
            substitute=[whitespaces_clean(s).upper() for s in substitute if s],
            bow=whitespaces_clean(bow).upper(),
        )

    ####################################################
    #                     GETTERS                      #
    ####################################################

    def get_name(self, selector: Selector) -> str:
        return whitespaces_clean(selector.xpath('//*[@id="main"]/div[2]/div[1]/h2/text()').get("")).upper()

    def get_date(self, selector: Selector) -> date:
        value = whitespaces_clean(selector.xpath('//*[@id="main"]/div[2]/div[2]/div[1]/div[1]/ul/li[1]/text()').get(""))
        value = value.replace("AGO", "AUG")  # want to avoid changing the local
        return datetime.strptime(value, "%d %b %Y").date()

    def get_day(self, selector: Selector) -> int:
        name = self.get_name(selector)
        if is_play_off(name):  # exception case
            return 1 if "1" in name else 2
        matches = re.findall(r"\d+ª día|\(\d+ª? JORNADA\)", name)
        return int(re.findall(r"\d+", matches[0])[0].strip()) if matches else 1

    def get_type(self, participants: List[Selector]) -> str:
        lanes = list(self.get_lane(p) for p in participants)
        return RACE_TIME_TRIAL if all(int(lane) == int(lanes[0]) for lane in lanes) else RACE_CONVENTIONAL

    def get_league(self, selector: Selector, is_female: bool) -> Optional[str]:
        if is_female:
            return "EMAKUMEZKO TRAINERUEN ELKARTEA"
        text = whitespaces_clean(selector.xpath('//*[@id="main"]/h1/span/text()').get("")).upper()
        if is_play_off(text):
            return "ASOCIACIÓN DE REMO DEL CANTÁBRICO"
        return re.sub(r"TEMPORADA \d+ GRUPO", "ASOCIACIÓN DE REMO DEL CANTÁBRICO", text)

    def get_town(self, selector: Selector) -> str:
        text = remove_parenthesis(selector.xpath('//*[@id="main"]/div[2]/div[2]/div[1]/div[1]/ul/li[4]/text()').get(""))
        text = text.replace(" Ver mapaOcultar mapa", "")
        return whitespaces_clean(text).upper()

    def get_race_lanes(self, selector: Selector) -> int:
        text = selector.xpath('//*[@id="main"]/div[2]/div[2]/div[1]/div[1]/ul/li[3]/text()').get("")
        if "CONTRARRELOJ" in text:
            return 1
        return int(re.findall(r"\d+", text)[0])

    def get_race_laps(self, selector: Selector) -> int:
        text = selector.xpath('//*[@id="main"]/div[2]/div[2]/div[1]/div[1]/ul/li[3]/text()').get("")
        return int(re.findall(r"\d+", text)[1])

    def is_cancelled(self, selector: Selector) -> bool:
        # race_id=260
        # try to find the "NO PUNTUABLE" text in the name
        return (
            "NO PUNTUABLE"
            in whitespaces_clean(selector.xpath('//*[@id="main"]/div[2]/div[1]/h2/text()').get("")).upper()
        )

    def get_participants(self, selector: Selector) -> List[Selector]:
        return [
            Selector(p)
            for p in selector.xpath('//*[@id="widget-resultados"]/div/div[3]/div/table[*]/tbody/tr').getall()
        ]

    def get_lane(self, participant: Selector) -> int:
        lane = participant.xpath("//*/th/text()").get("")
        return int(lane) if lane else 0

    def get_club_name(self, participant: Selector) -> str:
        name = participant.xpath("//*/td[1]/span/a/text()").get("")
        return whitespaces_clean(name).upper() if name else ""

    def get_distance(self, is_female: bool) -> int:
        return 2778 if is_female else 5556

    def get_laps(self, participant: Selector) -> List[str]:
        laps = participant.xpath("//*/td/text()").getall()
        return [t.strftime("%M:%S.%f") for t in [normalize_lap_time(e) for e in laps if e] if t is not None]

    def get_series(self, selector: Selector, participant: Selector) -> int:
        series = 1
        rows = [Selector(p) for p in selector.xpath('//*[@id="widget-resultados"]/div/div[3]/div/table').getall()]
        for row in rows:
            for p in row.xpath("//*/tbody/tr").getall():
                name = Selector(p).xpath("//*/td[1]/span/a/text()").get("")
                if participant.xpath("//*/td[1]/span/a/text()").get("") == name:
                    return series
            series += 1
        return 0

    ####################################################
    #                  NORMALIZATION                   #
    ####################################################

    @staticmethod
    def _normalize_race_name(name: str, is_female: bool = False) -> str:
        name = name.replace("AYTO", "AYUNTAMIENTO")
        name = name.replace("IKURRINA", "IKURRIÑA")
        name = name.replace(" AE ", "")
        name = re.sub(r"EXCMO|ILTMO", "", name)
        name = whitespaces_clean(name)

        # remove edition
        name = remove_roman(remove_parenthesis(whitespaces_clean(name)))
        # remove day
        name = re.sub(r"\d+ª día|\(\d+ª? JORNADA\)", "", name)

        if "-" in name:
            part1, part2 = whitespaces_clean(name.split("-")[0]), whitespaces_clean(name.split("-")[1])

            if any(e in part2 for e in ["OMENALDIA", "MEMORIAL"]):  # tributes
                name = part1
            if any(w in part1 for w in ["BANDERA", "BANDEIRA", "IKURRIÑA"]):
                name = part1

        name = normalize_trophy_name(name, is_female)

        return name

    @staticmethod
    def _hardcoded_name_edition_day(name: str, year: int, edition: int, day: int) -> Tuple[str, int, int]:
        if "AMBILAMP" in name:
            return "BANDERA AMBILAMP", edition, day
        if "BANDERA DE CASTRO" in name or "BANDERA CIUDAD DE CASTRO" in name:
            return "BANDERA DE CASTRO", edition, day
        if "CORREO" in name and "IKURRIÑA" in name:
            return "EL CORREO IKURRIÑA", (year - 1986), day
        if "DONIBANE ZIBURUKO" in name:
            return "DONIBANE ZIBURUKO ESTROPADAK", int(re.findall(r"\d+", name)[0]), 1
        if "SAN VICENTE DE LA BARQUERA" in name:
            return "BANDERA SAN VICENTE DE LA BARQUERA", edition, day

        match = re.match(r"\d+ª? JORNADA|JORNADA \d+", name)
        if match:
            arc = 1 if "1" in name else "2"
            return f"REGATA LIGA ARC {arc}", edition, int(re.findall(r"\d+", match.group(0))[0])

        if is_play_off(name):
            return "PLAY-OFF ARC", (year - 2005), day

        return name, edition, day
