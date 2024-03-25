import logging
import os
import re
from collections.abc import Generator
from datetime import date, datetime
from typing import Any, override

from parsel.selector import Selector

from pyutils.strings import remove_parenthesis, whitespaces_clean
from rscraping.data.constants import (
    CATEGORY_ABSOLUT,
    GENDER_FEMALE,
    GENDER_MALE,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from rscraping.data.functions import is_play_off
from rscraping.data.models import Datasource, Lineup, Participant, Race, RaceName
from rscraping.data.normalization.clubs import normalize_club_name
from rscraping.data.normalization.races import (
    find_race_sponsor,
    normalize_name_parts,
    normalize_race_name,
    remove_day_indicator,
)
from rscraping.data.normalization.times import normalize_lap_time
from rscraping.data.normalization.towns import normalize_town

from ._protocol import HtmlParser

logger = logging.getLogger(os.path.dirname(os.path.realpath(__file__)))


class ARCHtmlParser(HtmlParser):
    DATASOURCE = Datasource.ARC

    @override
    def parse_race(self, selector: Selector, *, race_id: str, is_female: bool, **_) -> Race | None:
        name = self.get_name(selector)
        if not name:
            logger.error(f"{self.DATASOURCE}: no race found for {race_id=}")
            return None
        logger.info(f"{self.DATASOURCE}: found race {name}")

        gender = GENDER_FEMALE if is_female else GENDER_MALE

        normalized_names = normalize_name_parts(normalize_race_name(name))
        if len(normalized_names) == 0:
            logger.error(f"{self.DATASOURCE}: unable to normalize {name=}")
            return None
        normalized_names = [(remove_day_indicator(n), e) for (n, e) in normalized_names]
        logger.info(f"{self.DATASOURCE}: race normalized to {normalized_names=}")

        participants = self.get_participants(selector)

        race = Race(
            name=self.get_name(selector),
            normalized_names=normalized_names,
            date=self.get_date(selector).strftime("%d/%m/%Y"),
            type=self.get_type(participants),
            day=self.get_day(selector),
            modality=RACE_TRAINERA,
            league=self.get_league(selector, is_female),
            town=self.get_town(selector),
            organizer=None,
            sponsor=find_race_sponsor(self.get_name(selector)),
            race_ids=[race_id],
            url=None,
            gender=gender,
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
                    category=CATEGORY_ABSOLUT,
                    club_name=self.get_club_name(row),
                    lane=self.get_lane(row),
                    series=self.get_series(selector, row),
                    laps=self.get_laps(row),
                    distance=self.get_distance(is_female),
                    handicap=None,
                    participant=normalize_club_name(self.get_club_name(row)),
                    race=race,
                    disqualified=self.is_disqualified(selector, row),
                )
            )

        return race

    @override
    def parse_race_ids(self, selector: Selector, **_) -> Generator[str, Any, Any]:
        urls = (
            selector.xpath('//*[@id="main"]/div[6]/table/tbody/tr[*]/td[2]/span/a/@href').getall()
            if selector.xpath('//*[@id="proximas-regatas"]').get()
            else selector.xpath('//*[@id="main"]/div[4]/table/tbody/tr[*]/td[2]/span/a/@href').getall()
        )
        return (url_parts[-2] for url_parts in (url.split("/") for url in urls))

    @override
    def parse_race_names(self, selector: Selector, **_) -> Generator[RaceName, Any, Any]:
        hrefs = (
            selector.xpath('//*[@id="main"]/div[6]/table/tbody/tr[*]/td[2]/span/a').getall()
            if selector.xpath('//*[@id="proximas-regatas"]').get()
            else selector.xpath('//*[@id="main"]/div[4]/table/tbody/tr[*]/td[2]/span/a').getall()
        )
        selectors = [Selector(h) for h in hrefs]
        pairs = [(s.xpath("//*/@href").get("").split("/")[-2], s.xpath("//*/text()").get("")) for s in selectors]
        return (RaceName(race_id=p[0], name=whitespaces_clean(p[1]).upper()) for p in pairs)

    def parse_club_ids(self, selector: Selector) -> Generator[str, Any, Any]:
        urls = (
            selector.xpath('//*[@id="main"]/div/div[2]/h2[*]/a/@href').getall()
            + selector.xpath('//*[@id="main"]/div/div[3]/h2[*]/a/@href').getall()
        )
        return (url_parts[-2] for url_parts in (url.split("/") for url in urls))

    @override
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
            race=normalize_race_name(race),
            club=normalize_club_name(club),
            coach=whitespaces_clean(coach.upper()),
            delegate=whitespaces_clean(delegate.upper()),
            coxswain=whitespaces_clean(coxswain.upper()),
            starboard=[whitespaces_clean(s).upper() for s in starboard if s],
            larboard=[whitespaces_clean(s).upper() for s in larboard if s],
            substitute=[whitespaces_clean(s).upper() for s in substitute if s],
            bow=whitespaces_clean(bow).upper(),
            images=[],
        )

    ####################################################
    #                     GETTERS                      #
    ####################################################

    def get_name(self, selector: Selector) -> str:
        return whitespaces_clean(selector.xpath('//*[@id="main"]/div[2]/div[1]/h2/text()').get("")).upper()

    def get_date(self, selector: Selector) -> date:
        value = whitespaces_clean(selector.xpath('//*[@id="main"]/div[2]/div[2]/div[1]/div[1]/ul/li[1]/text()').get(""))
        value = value.upper().replace("AGO", "AUG")  # want to avoid changing the local
        return datetime.strptime(value, "%d %b %Y").date()

    def get_day(self, selector: Selector) -> int:
        name = self.get_name(selector)
        if is_play_off(name):  # exception case
            return 1 if "1" in name or "I" in name.split() else 2
        matches = re.findall(r"\d+ª día|\(\d+ª? JORNADA\)", name)
        return int(re.findall(r"\d+", matches[0])[0].strip()) if matches else 1

    def get_type(self, participants: list[Selector]) -> str:
        lanes = list(self.get_lane(p) for p in participants)
        return RACE_TIME_TRIAL if all(int(lane) == int(lanes[0]) for lane in lanes) else RACE_CONVENTIONAL

    def get_league(self, selector: Selector, is_female: bool) -> str | None:
        if is_female:
            return "EMAKUMEZKO TRAINERUEN ELKARTEA"
        text = whitespaces_clean(selector.xpath('//*[@id="main"]/h1/span/span/text()').get("")).upper()
        if is_play_off(text):
            return "ASOCIACIÓN DE REMO DEL CANTÁBRICO"
        return text.replace("GRUPO", "ASOCIACIÓN DE REMO DEL CANTÁBRICO")

    def get_town(self, selector: Selector) -> str:
        text = remove_parenthesis(selector.xpath('//*[@id="main"]/div[2]/div[2]/div[1]/div[1]/ul/li[4]/text()').get(""))
        text = text.replace(" Ver mapaOcultar mapa", "")
        return normalize_town(text)

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

    def get_participants(self, selector: Selector) -> list[Selector]:
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

    def get_laps(self, participant: Selector) -> list[str]:
        laps = participant.xpath("//*/td/text()").getall()
        return [t.strftime("%M:%S.%f") for t in [normalize_lap_time(e) for e in laps if e] if t is not None]

    def is_disqualified(self, selector: Selector, participant: Selector) -> bool:
        # race_id=472
        # try to find a club with 0 points
        club_name = self.get_club_name(participant).upper()
        final_times_rows = selector.xpath('//*[@id="widget-resultados"]/div/div[1]/div[2]/div/table/tbody/tr')

        for row in final_times_rows:
            club_name_in_row = whitespaces_clean(row.xpath(".//td[1]/span/a/text()").get("")).upper()
            final_time = row.xpath(".//td[3]/text()").get("")

            if club_name_in_row == club_name:
                return final_time == "0"

        return False

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
