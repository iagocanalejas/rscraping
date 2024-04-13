import logging
import os
from collections.abc import Generator
from datetime import datetime
from typing import Any, override

from parsel.selector import Selector

from pyutils.strings import find_date, whitespaces_clean
from rscraping.data.checks import should_be_time_trial
from rscraping.data.constants import (
    CATEGORY_ABSOLUT,
    CATEGORY_SCHOOL,
    CATEGORY_VETERAN,
    GENDER_FEMALE,
    GENDER_MALE,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Datasource, Participant, Race, RaceName
from rscraping.data.normalization import (
    find_league,
    find_race_sponsor,
    normalize_club_name,
    normalize_lap_time,
    normalize_race_name,
    normalize_town,
)

from ._protocol import HtmlParser

logger = logging.getLogger(os.path.dirname(os.path.realpath(__file__)))


class MultiRaceException(Exception):
    pass


class TrainerasHtmlParser(HtmlParser):
    """
    - both race 'day' are saved in the same 'ref_id'
    - 'edition' can't be retrieved
    - 'league' can't be retrieved
    """

    DATASOURCE = Datasource.TRAINERAS

    _FEMALE = ["SF", "VF", "JF", "F"]
    _VETERAN = ["VF", "VM"]
    _SCHOOL = ["M", "JM", "JF", "CM", "CF"]
    _FILTERS = ["MEMORIAL", "CONTRARRELOJ", "DESCENSO", "ASCENSO", "CAMPEONATO", "TERESA HERRERA", "CONCHA"]

    @override
    def parse_race(self, selector: Selector, *, race_id: str, table: int | None = None, **_) -> Race | None:
        if self._races_count(selector) > 1 and not table:
            raise MultiRaceException()
        table = table or 1

        name = self.get_name(selector)
        if not name:
            logger.error(f"{self.DATASOURCE}: no race found for {race_id=}")
            return None
        logger.info(f"{self.DATASOURCE}: found race {name}")

        path = "div[1]/h2" if table == 1 else f"div[2]/h2[{table - 1}]"
        t_date = find_date(selector.xpath(f"/html/body/div[1]/main/div/div/div/{path}/text()").get(""))
        gender = self.get_gender(selector)
        distance = self.get_distance(selector)

        if not t_date:
            logger.error(f"{self.DATASOURCE}: no date found for {name=}")
            return None

        if not name:
            logger.error(f"{self.DATASOURCE}: no race found for {race_id=}")
            return None
        logger.info(f"{self.DATASOURCE}: race normalized to {name=}")

        participants = self.get_participants(selector, table)
        ttype = self.get_type(participants)
        ttype = ttype if not should_be_time_trial(name, t_date) else RACE_TIME_TRIAL
        category = self.get_category(selector)

        race = Race(
            name=name,
            normalized_names=[(self._normalize_race_name(normalize_race_name(name), name), None)],
            date=t_date.strftime("%d/%m/%Y"),
            type=ttype,
            day=self._clean_day(table, name),
            modality=RACE_TRAINERA,
            league=find_league(name),
            town=self.get_town(selector, race_table=table),
            organizer=None,
            sponsor=find_race_sponsor(self.get_name(selector)),
            race_ids=[race_id],
            url=None,
            gender=gender,
            datasource=self.DATASOURCE.value,
            cancelled=self.is_cancelled(participants),
            race_laps=self.get_race_laps(selector, table),
            race_lanes=self.get_race_lanes(participants),
            participants=[],
        )

        for row in participants:
            race.participants.append(
                Participant(
                    gender=gender,
                    category=category,
                    club_name=self.get_club_name(row),
                    lane=self.get_lane(row) if ttype == RACE_CONVENTIONAL else 1,
                    series=self.get_series(row) if ttype == RACE_CONVENTIONAL else 1,
                    laps=self.get_laps(row),
                    distance=distance,
                    handicap=None,
                    participant=normalize_club_name(self.get_club_name(row)),
                    race=race,
                    disqualified=self.is_disqualified(row),
                )
            )

        return race

    @override
    def parse_race_ids(
        self,
        selector: Selector,
        is_female: bool | None = None,
        category: str | None = None,
        **_,
    ) -> Generator[str, Any, Any]:
        for race in self.parse_race_names(selector, is_female=is_female, category=category):
            yield race.race_id

    @override
    def parse_race_names(
        self,
        selector: Selector,
        is_female: bool | None = None,
        category: str | None = None,
        **_,
    ) -> Generator[RaceName, Any, Any]:
        if category and category not in [CATEGORY_ABSOLUT, CATEGORY_VETERAN, CATEGORY_SCHOOL]:
            raise ValueError(f"invalid {category=}")

        rows = [Selector(r) for r in selector.xpath("/html/body/div[1]/div[2]/table/tbody/tr").getall()]
        for row in rows:
            ttype = row.xpath("//*/td[2]/text()").get("")
            if not self._has_gender(is_female, ttype) or not self._has_type(category, ttype):
                continue

            name = whitespaces_clean(row.xpath("//*/td[1]/a/text()").get("").upper())
            name = " ".join(n for n in name.split() if n != ttype)
            yield RaceName(race_id=row.xpath("//*/td[1]/a/@href").get("").split("/")[-1], name=name)

    def parse_flag_race_ids(self, selector: Selector, is_female: bool) -> Generator[str, Any, Any]:
        rows = selector.xpath(f"/html/body/main/div/div/div/div[{2 if is_female else 1}]/div/table/tr").getall()
        return (Selector(row).xpath("//*/td[3]/a/@href").get("").split("/")[-1] for row in rows[1:])

    def parse_club_race_ids(self, selector: Selector) -> Generator[str, Any, Any]:
        rows = selector.xpath("/html/body/div[1]/div[2]/div/table/tr").getall()
        return (Selector(row).xpath("//*/td[1]/a/@href").get("").split("/")[-1] for row in rows[1:])

    def parse_rower_race_ids(self, selector: Selector, year: str | None = None) -> Generator[str, Any, Any]:
        rows = selector.xpath("/html/body/main/section[2]/div/div/div[1]/div/table/tr/td/table/tr").getall()
        if not year:
            return (Selector(r).xpath("//*/td/a/@href").get("").split("/")[-1] for r in rows)

        return (
            Selector(r).xpath("//*/td/a/@href").get("").split("/")[-1]
            for r in rows
            if year in selector.xpath("//*/td[2]/text()").get("")
        )

    def parse_searched_flag_urls(self, selector: Selector) -> list[str]:
        return selector.xpath("/html/body/div[1]/div[2]/div/div/div[*]/div/div/div[2]/h5/a/@href").getall()

    def parse_flag_editions(self, selector: Selector, is_female: bool) -> Generator[tuple[int, int], Any, Any]:
        table = selector.xpath(f"/html/body/main/div/div/div/div[{2 if is_female else 1}]/div/table").get(None)
        if table:
            for row in Selector(table).xpath("//*/tr").getall()[1:]:
                parts = Selector(row).xpath("//*/td/text()").getall()
                yield (
                    datetime.strptime(whitespaces_clean(parts[1]), "%d-%m-%Y").date().year,
                    int(whitespaces_clean(parts[0])),
                )

    def get_number_of_pages(self, selector: Selector) -> int:
        return len(selector.xpath("/html/body/div[1]/div[3]/nav/ul/li[*]").getall()) - 2

    ####################################################
    #                     GETTERS                      #
    ####################################################

    def get_name(self, selector: Selector) -> str:
        name = whitespaces_clean(selector.xpath("/html/body/div[1]/div/h1/text()").get("")).upper()
        name = " ".join(name.split()[:-1])
        return name

    def get_gender(self, selector: Selector) -> str:
        parts = selector.xpath("/html/body/div[1]/main/div/div/div/div[1]/h2/text()").get("")
        part = whitespaces_clean(parts.split(" - ")[-1])
        return GENDER_FEMALE if part in self._FEMALE else GENDER_MALE

    def get_type(self, participants: list[Selector]) -> str:
        series = [s for s in [p.xpath("//*/td[4]/text()").get("") for p in participants] if s]
        return RACE_TIME_TRIAL if len(set(series)) == len(series) else RACE_CONVENTIONAL

    def get_category(self, selector: Selector) -> str:
        subtitle = selector.xpath("/html/body/div[1]/main/div/div/div/div[1]/h2/text()").get("").upper()
        category = whitespaces_clean(subtitle.split("-")[-1])
        if category in self._VETERAN:
            return CATEGORY_VETERAN
        if category in self._SCHOOL:
            return CATEGORY_SCHOOL
        return CATEGORY_ABSOLUT

    def get_town(self, selector: Selector, race_table: int) -> str:
        parts = selector.xpath(f"/html/body/div[1]/main/div/div/div/div[{race_table}]/h2/text()").get("")
        return normalize_town(whitespaces_clean(parts.split(" - ")[0]))

    def get_race_lanes(self, participants: list[Selector]) -> int | None:
        if self.get_type(participants) == RACE_TIME_TRIAL:
            return 1
        lanes = list(self.get_lane(p) for p in participants)
        lanes = {int(lane) for lane in lanes if lane is not None}
        return len(lanes) if lanes else None

    def get_race_laps(self, selector: Selector, table: int) -> int:
        cia = []
        for participant in self.get_participants(selector, table):
            participant_cia = participant.xpath("//*/td/text()").getall()
            cia.append([p for p in participant_cia if ":" in p])
        return len(max(cia, key=len))

    def is_cancelled(self, participants: list[Selector]) -> bool:
        # race_id=4061|211
        laps = [self.get_laps(p) for p in participants if not self.is_disqualified(p)]
        return len([lap for lap in laps if len(lap) == 0]) >= len(participants) // 2

    def get_participants(self, selector: Selector, table: int) -> list[Selector]:
        rows = selector.xpath(f"{self._participants_path(selector)}[{table}]/tr").getall()
        return [Selector(t) for t in rows[1:]]

    def get_lane(self, participant: Selector) -> int | None:
        lane = participant.xpath("//*/td[3]/text()").get()
        return int(lane) if lane else None

    def get_club_name(self, participant: Selector) -> str:
        name = participant.xpath("//*/td[2]/text()").get()
        return whitespaces_clean(name).upper() if name else ""

    def get_distance(self, selector: Selector) -> int | None:
        parts = whitespaces_clean(selector.xpath("/html/body/div[1]/main/div/div/div/div[1]/h2/text()").get(""))
        parts = parts.split(" - ")
        part = next((p for p in parts if "metros" in p), None)
        return int(part.replace(" metros", "")) if part is not None else None

    def get_laps(self, participant: Selector) -> list[str]:
        laps = [e for e in participant.xpath("//*/td/text()").getall() if ":" in e]
        return [t.strftime("%M:%S.%f") for t in [normalize_lap_time(e) for e in laps if e] if t is not None]

    def is_disqualified(self, participant: Selector) -> bool:
        # race_id=5360|5535
        # try to find the "Desc." text in the final crono
        laps = participant.xpath("//*/td/text()").getall()[2:-4]
        return any("Desc." in lap or "FR" in lap for lap in laps)

    def get_series(self, participant: Selector) -> int:
        series = participant.xpath("//*/td[4]/text()").get()
        return int(series) if series else 0

    ####################################################
    #                     PRIVATE                      #
    ####################################################

    def _races_count(self, selector: Selector) -> int:
        return len(selector.xpath(f"{self._participants_path(selector)}[*]").getall())

    def _has_gender(self, is_female: bool | None, value: str) -> bool:
        return is_female is None or (value in self._FEMALE if is_female else value not in self._FEMALE)

    def _has_type(self, category: str | None, value: str) -> bool:
        if not category:
            return True
        if category == CATEGORY_ABSOLUT:
            return value not in self._VETERAN and value not in self._SCHOOL
        if category == CATEGORY_VETERAN:
            return value in self._VETERAN
        if category == CATEGORY_SCHOOL:
            return value in self._SCHOOL
        return False

    def _clean_day(self, table: int, name: str) -> int:
        if "TERESA" in name and "HERRERA" in name:
            return 1
        return table

    @staticmethod
    def _participants_path(selector: Selector) -> str:
        path = "/html/body/div[1]/main/div[1]/div/div/div[2]/table"
        if not selector.xpath(path):
            # race_id=5706
            path = "/html/body/div[1]/main/div[1]/div/div/div[3]/table"
        return path

    @staticmethod
    def _normalize_race_name(name: str, original_name: str) -> str:
        if all(n in name for n in ["ILLA", "SAMERTOLAMEU"]) and "FANDICOSTA" in original_name:
            # HACK: this is a weird flag case in witch Meira restarted the edition for his 'B' team.
            return "BANDERA ILLA DO SAMERTOLAMEU - FANDICOSTA"

        return name
