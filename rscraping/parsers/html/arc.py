import logging
import os
import re
from collections.abc import Generator
from datetime import date, datetime
from typing import override

from parsel.selector import Selector

from pyutils.strings import find_date, remove_parenthesis, whitespaces_clean
from rscraping.data.checks import is_play_off
from rscraping.data.constants import (
    CATEGORY_ABSOLUT,
    GENDER_FEMALE,
    GENDER_MALE,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Datasource, Participant, Penalty, Race, RaceName
from rscraping.data.normalization import (
    ensure_b_teams_have_the_main_team_racing,
    find_race_sponsor,
    normalize_club_name,
    normalize_lap_time,
    normalize_name_parts,
    normalize_race_name,
    normalize_town,
    remove_day_indicator,
)

from ._protocol import HtmlParser

logger = logging.getLogger(os.path.dirname(os.path.realpath(__file__)))


class ARCHtmlParser(HtmlParser):
    DATASOURCE = Datasource.ARC

    @override
    def parse_race(self, selector: Selector, *, race_id: str, is_female: bool, **_) -> Race:
        name = self.get_name(selector)
        assert name, f"{self.DATASOURCE}: no name found for {race_id=}"

        t_date = self.get_date(selector)
        assert t_date is not None, f"{self.DATASOURCE}: no date found for {race_id=}"

        normalized_names = normalize_name_parts(normalize_race_name(name))
        normalized_names = [(remove_day_indicator(n), e) for (n, e) in normalized_names]
        assert len(normalized_names) > 0, f"{self.DATASOURCE}: unable to normalize {name=}"
        logger.info(f"{self.DATASOURCE}: found race {t_date}::{name}")

        gender = GENDER_FEMALE if is_female else GENDER_MALE
        participants = self.get_participants(selector)

        race = Race(
            name=self.get_name(selector),
            normalized_names=normalized_names,
            date=t_date.strftime("%d/%m/%Y"),
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
            category=CATEGORY_ABSOLUT,
            datasource=self.DATASOURCE.value,
            cancelled=self.is_cancelled(selector),
            race_laps=self.get_race_laps(selector),
            race_lanes=self.get_race_lanes(selector),
            participants=[],
        )

        for row in participants:
            disqualified = self.is_disqualified(selector, row)
            penalty = Penalty(reason=None, disqualification=disqualified) if disqualified else None
            participant_name = normalize_club_name(self.get_club_name(row))
            if "CASTRO " in participant_name:
                # HACK: CASTRO URDIALES, CASTRO and CASTREÑA differentiation
                if t_date.year < 2013:
                    participant_name = "CASTRO URDIALES"
                else:
                    if any(w in self.get_club_name(row) for w in ["A.N. ", "AN ", "AN. "]):
                        participant_name = "CASTRO"
                    else:
                        participant_name = "CASTREÑA"
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
                    participant=participant_name,
                    race=race,
                    penalty=penalty,
                    absent=False,
                    retired=False,
                    guest=False,
                )
            )

        ensure_b_teams_have_the_main_team_racing(race)

        return race

    @override
    def parse_race_ids(self, selector: Selector, **_) -> Generator[str]:
        urls = (
            selector.xpath('//*[@id="main"]/div[6]/table/tbody/tr[*]/td[2]/span/a/@href').getall()
            if selector.xpath('//*[@id="proximas-regatas"]').get()
            else selector.xpath('//*[@id="main"]/div[4]/table/tbody/tr[*]/td[2]/span/a/@href').getall()
        )
        return (url_parts[-2] for url_parts in (url.split("/") for url in urls))

    @override
    def parse_race_ids_by_days(self, selector: Selector, days: list[datetime], **kwargs) -> Generator[str]:
        assert len(days) > 0, "days must have at least one element"
        assert all(d.year == days[0].year for d in days), "all days must be from the same year"

        def _find_date(s: Selector) -> datetime | None:
            maybe_date = f"{whitespaces_clean(s.xpath('//*/td[1]/span/text()').get('')).upper()} {days[0].year}"
            found_date = find_date(maybe_date, day_first=True)
            return datetime.combine(found_date, datetime.min.time()) if found_date else None

        rows = (
            selector.xpath('//*[@id="main"]/div[6]/table/tbody/tr[*]').getall()
            if selector.xpath('//*[@id="proximas-regatas"]').get()
            else selector.xpath('//*[@id="main"]/div[4]/table/tbody/tr[*]').getall()
        )
        selectors = [Selector(h) for h in rows]
        return (s.xpath("//*/td[2]/span/a/@href").get("").split("/")[-2] for s in selectors if _find_date(s) in days)

    @override
    def parse_race_names(self, selector: Selector, **_) -> Generator[RaceName]:
        hrefs = (
            selector.xpath('//*[@id="main"]/div[6]/table/tbody/tr[*]/td[2]/span/a').getall()
            if selector.xpath('//*[@id="proximas-regatas"]').get()
            else selector.xpath('//*[@id="main"]/div[4]/table/tbody/tr[*]/td[2]/span/a').getall()
        )
        selectors = [Selector(h) for h in hrefs]
        return (
            RaceName(
                race_id=s.xpath("//*/@href").get("").split("/")[-2],
                name=whitespaces_clean(s.xpath("//*/text()").get("")).upper(),
            )
            for s in selectors
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
            if "1" in name or "I" in name.split():
                return 1
            return 2 if self.get_date(selector).isoweekday() == 7 else 1  # 2 for sunday
        matches = re.findall(r"\d+ª día|\(\d+ª? JORNADA\)", name)
        if matches:
            matches = re.findall(r"\d+", matches[0])[0].strip()
            return int(matches) if matches <= 2 else 1
        return 1

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
