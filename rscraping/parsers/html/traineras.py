import logging
import os
from collections import Counter
from collections.abc import Generator
from datetime import date, datetime
from typing import override

from parsel.selector import Selector

from pyutils.strings import find_date, whitespaces_clean
from rscraping.data.checks import is_branch_club, should_be_time_trial
from rscraping.data.constants import (
    CATEGORY_ABSOLUT,
    CATEGORY_SCHOOL,
    CATEGORY_VETERAN,
    GENDER_FEMALE,
    GENDER_MALE,
    GENDER_MIX,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Club, Datasource, Participant, Penalty, Race, RaceName
from rscraping.data.normalization import (
    ensure_b_teams_have_the_main_team_racing,
    find_league,
    find_race_sponsor,
    is_absent,
    is_cancelled,
    is_guest,
    is_retired,
    normalize_club_name,
    normalize_lap_time,
    normalize_name_parts,
    normalize_penalty,
    normalize_race_name,
    normalize_town,
    retrieve_penalty_times,
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
    _MIX = ["M"]
    _VETERAN = ["VF", "VM"]
    _SCHOOL = ["JM", "JF", "CM", "CF"]

    @override
    def parse_race(self, selector: Selector, *, race_id: str, table: int | None = None, **_) -> Race:
        if self._races_count(selector) > 1 and not table:
            logger.error(f"{self.DATASOURCE}: multiple races found for {race_id=} without specifying a table")
            raise MultiRaceException("no table specified")
        table = table or 1

        name = self.get_name(selector)
        assert name, f"{self.DATASOURCE}: no name found for {race_id=}"

        t_date = self.get_date(selector, table)
        assert t_date is not None, f"{self.DATASOURCE}: no date found for {race_id=}"

        normalized_names = normalize_name_parts(normalize_race_name(name))
        normalized_names = [(self._normalizations(n, name, t_date), e) for (n, e) in normalized_names]
        assert len(normalized_names) > 0, f"{self.DATASOURCE}: unable to normalize {name=}"
        logger.info(f"{self.DATASOURCE}: found race {t_date}::{name}")

        gender = self.get_gender(selector)
        category = self.get_category(selector)
        distance = self.get_distance(selector)

        participants = self.get_participants(selector, table)
        race_lanes = self.get_race_lanes(participants)
        race_notes = self.get_race_notes(selector)
        ttype = self.get_type(participants) if not should_be_time_trial(name, t_date) else RACE_TIME_TRIAL

        race = Race(
            name=name,
            normalized_names=normalized_names,
            date=t_date.strftime("%d/%m/%Y"),
            type=ttype,
            day=self._clean_day(table, name),
            modality=RACE_TRAINERA,
            league=find_league(name),
            town=self.get_town(selector, table=table),
            organizer=None,
            sponsor=find_race_sponsor(self.get_name(selector)),
            race_ids=[race_id],
            url=None,
            gender=gender,
            category=category,
            datasource=self.DATASOURCE.value,
            cancelled=self.is_cancelled(participants) or is_cancelled(race_notes),
            race_laps=self.get_race_laps(selector, table),
            race_lanes=race_lanes,
            race_notes=race_notes,
            participants=[],
        )

        participant_names = [normalize_club_name(self.get_club_name(row)) for row in participants]
        extra_times = retrieve_penalty_times(race_notes) if race_notes else {}
        penalties = normalize_penalty(race_notes, participants=participant_names)

        if any(k == "" for k in penalties.keys()) and len(extra_times) == 0:
            penalties[list(extra_times.keys())[0]] = penalties[""]
            penalties.pop("")
        if any(k == "" for k in extra_times.keys()) and len(penalties) == 0:
            extra_times[list(extra_times.keys())[0]] = extra_times[""]
            extra_times.pop("")

        if "" in extra_times:
            logger.warning(f"{self.DATASOURCE}: no participant found for extra time:\n\t{extra_times['']}")
        if "" in penalties:
            logger.warning(f"{self.DATASOURCE}: no participant found for penalty:\n\t{penalties['']}")
        if race_notes and not penalties:
            logger.warning(f"{self.DATASOURCE}: no penalties found for note:\n\t{race_notes}")

        for row in participants:
            participant_name = normalize_club_name(self.get_club_name(row))
            participant_name = self._fix_castro_mess(participant_name, self.get_club_name(row), t_date)

            laps = self.get_laps(row)
            time = extra_times.get(participant_name, None)
            penalty = penalties.get(participant_name, None)

            if time:
                laps.append(time.strftime("%M:%S.%f"))

            if penalty:
                penalty.disqualification = self.is_disqualified(row) or penalty.disqualification
            elif self.is_disqualified(row):
                penalty = Penalty(reason=None, disqualification=True)

            race.participants.append(
                Participant(
                    gender=gender,
                    category=category,
                    club_name=self.get_club_name(row),
                    lane=self.get_lane(row) if ttype == RACE_CONVENTIONAL else 1,
                    series=self.get_series(row) if ttype == RACE_CONVENTIONAL else 1,
                    laps=laps,
                    distance=distance,
                    handicap=None,
                    participant=participant_name,
                    race=race,
                    penalty=penalty,
                    retired=self.has_retired(row) or is_retired(participant_name, race_notes),
                    absent=is_absent(participant_name, race_notes),
                    guest=is_guest(participant_name, race_notes),
                )
            )

        ensure_b_teams_have_the_main_team_racing(race)

        return race

    @override
    def parse_race_ids(self, selector: Selector, **_) -> Generator[str]:
        return (race.race_id for race in self.parse_race_names(selector))

    @override
    def parse_race_ids_by_days(self, selector: Selector, days: list[datetime], **kwargs) -> Generator[str]:
        assert len(days) > 0, "days must have at least one element"
        assert all(d.year == days[0].year for d in days), "all days must be from the same year"

        rows = [Selector(r) for r in selector.xpath("/html/body/div[1]/div[2]/table/tbody/tr").getall()]
        for row in rows:
            ttype = row.xpath("//*/td[2]/text()").get("")
            name = whitespaces_clean(row.xpath("//*/td[1]/a/text()").get("").upper())
            name = " ".join(n for n in name.split() if n != ttype)
            if datetime.strptime(row.xpath("//*/td[5]/text()").get(""), "%d-%m-%Y") in days:
                yield row.xpath("//*/td[1]/a/@href").get("").split("/")[-1]

    @override
    def parse_race_names(self, selector: Selector, **_) -> Generator[RaceName]:
        rows = [Selector(r) for r in selector.xpath("/html/body/div[1]/div[2]/table/tbody/tr").getall()]
        for row in rows:
            ttype = row.xpath("//*/td[2]/text()").get("")
            name = whitespaces_clean(row.xpath("//*/td[1]/a/text()").get("").upper())
            name = " ".join(n for n in name.split() if n != ttype)
            yield RaceName(race_id=row.xpath("//*/td[1]/a/@href").get("").split("/")[-1], name=name)

    def parse_flag_race_ids(self, selector: Selector, gender: str, category: str, **_) -> Generator[str]:
        table = self._get_matching_flag_table(gender, category, selector)
        if table:
            rows = Selector(table).xpath("//*/tr").getall()
            yield from (Selector(row).xpath("//*/td[3]/a/@href").get("").split("/")[-1] for row in rows[1:])

    def parse_club_race_ids(self, selector: Selector) -> Generator[str]:
        rows = selector.xpath("/html/body/div[1]/div[2]/div/table/tr").getall()
        return (Selector(row).xpath("//*/td[1]/a/@href").get("").split("/")[-1] for row in rows[1:])

    def parse_rower_race_ids(self, selector: Selector, year: str | None = None) -> Generator[str]:
        rows = selector.xpath("/html/body/main/section[2]/div/div/div[1]/div/table/tr/td/table/tr").getall()
        if not year:
            return (Selector(r).xpath("//*/td/a/@href").get("").split("/")[-1] for r in rows)

        return (
            Selector(r).xpath("//*/td/a/@href").get("").split("/")[-1]
            for r in rows
            if year in selector.xpath("//*/td[2]/text()").get("")
        )

    def parse_club_details(self, selector: Selector, **_) -> Club | None:
        name = whitespaces_clean(selector.xpath("/html/body/main/section[1]/div/div[2]/h1/text()").get("").upper())
        if not name:
            return None

        year = selector.xpath("/html/body/main/section[1]/div/div[2]/div[1]/div[1]/span/text()").get("")
        year = whitespaces_clean(year)
        if not year.isdigit():
            year = None

        return Club(
            name=name,
            normalized_name=normalize_club_name(name),
            datasource=self.DATASOURCE.value,
            founding_year=year,
        )

    def parse_searched_flag_urls(self, selector: Selector) -> list[str]:
        return selector.xpath("/html/body/div[1]/div[2]/div/div/div[*]/div/div/div[2]/h5/a/@href").getall()

    def parse_flag_editions(self, selector: Selector, gender: str, category: str) -> Generator[tuple[int, int]]:
        table = self._get_matching_flag_table(gender, category, selector)
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

    def get_date(self, selector: Selector, table: int) -> date | None:
        title = self._get_race_title(selector, table)
        return find_date(title)

    def get_gender(self, selector: Selector) -> str:
        parts = selector.xpath("/html/body/div[1]/main/div/div/div/div[1]/h2/text()").get("")
        part = whitespaces_clean(parts.split(" - ")[-1])
        if part in self._MIX:
            return GENDER_MIX
        if part in self._FEMALE:
            return GENDER_FEMALE
        return GENDER_MALE

    def get_type(self, participants: list[Selector]) -> str:
        series = [self.get_series(p) for p in participants]
        series = [s for s in series if s]
        if len(set(series)) == len(series):
            # series column is indicating start order
            return RACE_TIME_TRIAL

        lanes = [self.get_lane(p) for p in participants]
        lanes = [lane for lane in lanes if lane]
        if len(set(lanes)) == 1 and len(participants) > 1:
            # all participants are racing in the same lane
            return RACE_TIME_TRIAL

        return RACE_CONVENTIONAL

    def get_category(self, selector: Selector) -> str:
        subtitle = selector.xpath("/html/body/div[1]/main/div/div/div/div[1]/h2/text()").get("").upper()
        category = whitespaces_clean(subtitle.split("-")[-1])
        if category in self._VETERAN:
            return CATEGORY_VETERAN
        if category in self._SCHOOL:
            return CATEGORY_SCHOOL
        return CATEGORY_ABSOLUT

    def get_town(self, selector: Selector, table: int) -> str:
        parts = self._get_race_title(selector, table)
        return normalize_town(whitespaces_clean(parts.split(" - ")[0]))

    def get_race_lanes(self, participants: list[Selector]) -> int | None:
        if self.get_type(participants) == RACE_TIME_TRIAL:
            return 1
        lanes = list(self.get_lane(p) for p in participants)
        lanes = {int(lane) for lane in lanes if lane is not None}
        if lanes:
            return len(lanes)

        # try to count the number of participants in each serie
        series = Counter([int(self.get_series(p)) for p in participants])
        lanes = max(series.values())
        if all(v == lanes or v == (lanes - 1) for v in series.values()):
            return lanes
        return None

    def get_race_laps(self, selector: Selector, table: int) -> int | None:
        cia = []
        for participant in self.get_participants(selector, table):
            participant_cia = participant.xpath("//*/td/text()").getall()
            cia.append([p for p in participant_cia if ":" in p])
        return len(max(cia, key=len)) if cia else None

    def is_cancelled(self, participants: list[Selector]) -> bool:
        # race_id=4061|211
        laps = [self.get_laps(p) for p in participants if not self.is_disqualified(p)]
        return len([lap for lap in laps if len(lap) == 0]) >= len(participants) // 2

    def get_participants(self, selector: Selector, table: int) -> list[Selector]:
        modifier = 1 if self._has_label(selector) else 0
        rows = selector.xpath(f"/html/body/div[1]/main/div/div/div/div[{(table * 2) + modifier}]/table/tr").getall()
        return [Selector(t) for t in rows[1:]]

    def get_lane(self, participant: Selector) -> int | None:
        lane = participant.xpath("//*/td[3]/text()").get()
        return int(lane) if lane and int(lane) <= 6 else None

    def get_club_name(self, participant: Selector) -> str:
        name = participant.xpath("//*/td[2]/text()").get()
        return whitespaces_clean(name).upper() if name else ""

    def get_distance(self, selector: Selector) -> int | None:
        parts = whitespaces_clean(selector.xpath("/html/body/div[1]/main/div/div/div/div[1]/h2/text()").get(""))
        parts = parts.split(" - ")
        part = next((p for p in parts if "metros" in p), None)
        return int(part.replace(" metros", "")) if part is not None else None

    def get_laps(self, participant: Selector) -> list[str]:
        laps = [e for e in participant.xpath("//*/td/text()").getall() if any(c in e for c in [":", ".", ","])]
        return [t.strftime("%M:%S.%f") for t in [normalize_lap_time(e) for e in laps if e] if t is not None]

    def is_disqualified(self, participant: Selector) -> bool:
        # race_id=5360|5535
        # try to find the "Desc." text in the final crono
        laps = participant.xpath("//*/td/text()").getall()[2:-4]
        return any(w in lap for w in ["Desc.", "FR"] for lap in laps)

    def has_retired(self, participant: Selector) -> bool:
        # race_id=5360|5535
        # try to find the "Desc." text in the final crono
        laps = participant.xpath("//*/td/text()").getall()[2:-4]
        return any(w in lap for w in ["Ret."] for lap in laps)

    def get_series(self, participant: Selector) -> int:
        series = participant.xpath("//*/td[4]/text()").get()
        return int(series) if series else 0

    def get_race_notes(self, selector: Selector) -> str | None:
        notes = selector.xpath("/html/body/div[1]/main/div[2]/div[2]/div/text()").get(None)
        return whitespaces_clean(notes) if notes else None

    ####################################################
    #                     PRIVATE                      #
    ####################################################

    def _has_label(self, selector: Selector) -> bool:
        target_div = selector.xpath("/html/body/div[1]/main/div/div/div/div[2]")
        return bool(target_div[0].xpath(".//p"))

    def _get_race_title(self, selector: Selector, table: int) -> str:
        modifier = 0 if self._has_label(selector) and table > 1 else 1
        date_path = f"div[{(table * 2) - modifier}]/h2"
        return selector.xpath(f"/html/body/div[1]/main/div/div/div/{date_path}/text()").get("")

    def _races_count(self, selector: Selector) -> int:
        tables = selector.xpath("/html/body/div[1]/main/div/div/div/div[*]/table").getall()
        return len(tables)

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

    def _get_matching_flag_table(self, gender: str, category: str, selector: Selector) -> str | None:
        """
        Returns the table that matches the gender|category combination we want.
        """
        words = []
        if gender == GENDER_MALE:
            if category == CATEGORY_ABSOLUT:
                words = ["SÉNIOR", "MASCULINO"]
            elif category == CATEGORY_VETERAN:
                words = ["VETERANO", "MASCULINO"]
            elif category == CATEGORY_SCHOOL:
                words = ["JUVENIL", "MASCULINO"]
        elif gender == GENDER_FEMALE:
            if category == CATEGORY_ABSOLUT:
                words = ["SÉNIOR", "FEMENINO"]
            elif category == CATEGORY_VETERAN:
                words = ["VETERANO", "FEMENINO"]
            elif category == CATEGORY_SCHOOL:
                words = ["JUVENIL", "FEMENINO"]
        else:
            words = ["MIXTO"]

        titles = selector.xpath("/html/body/main/div/div/div/div[*]/h2/text()").getall()
        idx = next((i for i, t in enumerate(titles) if all(w in t for w in words)), -1)
        return selector.xpath(f"/html/body/main/div/div/div/div[{idx + 1}]/div/table").get(None) if idx >= 0 else None

    @staticmethod
    def _normalizations(name: str, original_name: str, t_date: date) -> str:
        if all(n in name for n in ["ILLA", "SAMERTOLAMEU"]) and "FANDICOSTA" in original_name:
            # HACK: this is a weird flag case in witch Meira restarted the edition for his 'B' team.
            return "BANDERA ILLA DO SAMERTOLAMEU - FANDICOSTA"

        if all(n in name for n in ["TERESA", "HERRERA"]):
            return "TROFEO TERESA HERRERA" if t_date.isoweekday() == 7 else "TROFEO TERESA HERRERA (CLASIFICATORIA)"

        if all(n in name for n in ["GRAN", "PREMIO", "ASTILLERO"]) and t_date.year > 2018:
            return "BANDERA DEL REAL ASTILLERO DE GUARNIZO"

        return name

    @staticmethod
    def _fix_castro_mess(participant_name: str, club_name: str, t_date: date) -> str:
        # HACK: CASTRO URDIALES, CASTRO and CASTREÑA differentiation
        if "CASTRO " in participant_name or "CASTREÑA" in participant_name:
            branch = ""
            if is_branch_club(participant_name):
                branch = " B"
            if is_branch_club(participant_name, letter="C"):
                branch = " C"

            if t_date.year < 2013:
                return "CASTRO URDIALES" + branch
            else:
                if any(w in club_name for w in ["A.N. ", "AN ", "AN. "]):
                    return "CASTRO" + branch
                else:
                    return "CASTREÑA" + branch
        return participant_name
