import re
from collections.abc import Generator
from datetime import date, datetime
from typing import Any

import inquirer
from pandas import DataFrame, Series
from pandas.core.series import NDFrame

from pyutils.strings import find_date, remove_symbols, whitespaces_clean
from rscraping.data.constants import (
    CATEGORY_ABSOLUT,
    CATEGORY_VETERAN,
    GENDER_FEMALE,
    GENDER_MALE,
    GENDER_MIX,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Datasource, Participant, Race
from rscraping.data.normalization.clubs import normalize_club_name
from rscraping.data.normalization.races import normalize_name_parts, normalize_race_name
from rscraping.data.normalization.times import normalize_lap_time, normalize_spanish_months

from ._parser import DataFrameParser


class InforemoDataFrameParser(DataFrameParser, source=Datasource.INFOREMO):
    DATASOURCE = Datasource.INFOREMO

    _GENDERS = {
        GENDER_MALE: ["MASCULINO", "ABSOLUTO", "VETERANO"],
        GENDER_FEMALE: ["FEMENINO", "VETERANA"],
        GENDER_MIX: ["MIXTO"],
    }

    def parse_races_from(
        self, data: DataFrame, *_, file_name: str, header: str, manual_input: bool = False, **__
    ) -> Generator[Race, Any, Any]:
        name = self._try_find_race_name(header, manual_input=manual_input)
        t_date = self._try_find_race_date(header, manual_input=manual_input)
        if not name:
            raise ValueError(f"{self.DATASOURCE}: no name found")
        if not t_date:
            raise ValueError(f"{self.DATASOURCE}: no date found")

        df = self._clean_dataframe(data)

        race_laps = self.get_race_laps(df)

        identifiers = df[2].unique()
        for identifier in [i for i in identifiers if i]:
            participants: NDFrame = df[df[2] == identifier]

            genders = [self.get_gender(p) for (_, p) in participants.iterrows()]
            gender = (
                genders[0]
                if all(g == genders[0] for g in genders) and genders[0] in [GENDER_MALE, GENDER_FEMALE, GENDER_MIX]
                else None
            )

            race_lanes = self.get_race_lanes(participants)

            race = Race(
                name=name,
                normalized_names=normalize_name_parts(name),
                date=t_date.strftime("%d/%m/%Y"),
                type=RACE_CONVENTIONAL if race_lanes > 1 else RACE_TIME_TRIAL,
                day=1,
                modality=RACE_TRAINERA,
                league=None,
                town=None,
                organizer=None,
                sponsor=None,
                race_id=file_name,
                url=None,
                gender=gender,
                datasource=self.DATASOURCE.value,
                cancelled=False,
                race_laps=race_laps,
                race_lanes=race_lanes,
                participants=[],
            )

            race.participants = self._get_race_participants(participants, race)

            yield race

    def _get_race_participants(self, participants: NDFrame, race: Race) -> list[Participant]:
        items: list[Participant] = []
        for _, participant in participants.iterrows():
            club_name = self.get_club_name(participant)
            items.append(
                Participant(
                    gender=self.get_gender(participant, club_name),
                    category=self.get_category(participant),
                    club_name=club_name,
                    lane=self.get_lane(participant),
                    series=self.get_series(participant),
                    laps=self.get_laps(participant),
                    distance=5556,
                    handicap=None,
                    participant=normalize_club_name(self.get_club_name(participant)),
                    race=race,
                    disqualified=False,
                )
            )
        return items

    def _try_find_race_name(self, data: str, manual_input: bool) -> str | None:
        name = None
        for part in data.split("\n"):
            if not part or any(w in part for w in ["@", "inforemo"]):
                continue
            # check if any 4 letter convination of "inforemobancofijo" is present in the part and discard it
            if any("inforemobancofijo"[i : i + 4] in part for i in range(len("inforemobancofijo") - 3)):
                continue

            match = re.match(r"^[\wñÑ\- ]+$", remove_symbols(part))
            if match and len(match.group(0)) > 5 and (not name or len(part) > len(name)):
                name = normalize_race_name(part)

        if not name and manual_input:
            name = inquirer.text(message=f"no name found \n {data} \n set manual name for race:")

        return name

    def _try_find_race_date(self, data: str, manual_input: bool) -> date | None:
        t_date = None
        for part in data.split("\n"):
            if not part or any(w in part for w in ["@", "inforemo"]):
                continue

            phrase = remove_symbols(normalize_spanish_months(part))
            t_date = find_date(phrase, language="es_ES.utf8")

            if t_date:
                break

        if not t_date and manual_input:
            t_date = inquirer.text(message=f"no date found \n {data} \n set manual date for race (DD-MM-YYYY):")
            t_date = datetime.strptime("%d-%m-%Y", t_date).date() if t_date else None

        return t_date

    ####################################################
    #                      GETTERS                     #
    ####################################################

    def get_club_name(self, data: Series) -> str:
        return str(data[1])

    def get_lane(self, data: Series) -> int:
        try:
            # if : means we are in a TIME_TRIAL image so all the boats will be in the same lane
            return 1 if ":" in data[4] else int(data[4])
        except ValueError:
            return 1

    def get_series(self, data: Series) -> int | None:
        try:
            return int(data[3])
        except ValueError:
            return None

    @staticmethod
    def clean_lap(maybe_tyme: str) -> str:
        # clean normal OCR errors
        maybe_tyme = maybe_tyme.replace('"a', "4:").replace("T", "").replace("_", "")
        maybe_tyme = maybe_tyme.replace("::", ":")

        return whitespaces_clean(maybe_tyme)

    def get_laps(self, data: Series) -> list[str]:
        idx = 3 if ":" in data[4] else 4
        return [t.isoformat() for t in [normalize_lap_time(self.clean_lap(t)) for t in data.iloc[idx:]] if t]

    def get_gender(self, data: Series, club_name: str | None = None) -> str:
        if club_name and "MIXTO" in club_name.upper():
            return GENDER_MIX

        gender = str(data[2])
        for k, v in self._GENDERS.items():
            if gender in v or any(part in gender for part in v):
                return k
        return gender

    def get_category(self, data: Series) -> str:
        modality = data[2]
        if any(e in modality for e in ["VETERANO", "VETERANA"]):
            return CATEGORY_VETERAN
        return CATEGORY_ABSOLUT

    def get_race_lanes(self, df: NDFrame) -> int:
        return max(self.get_lane(p) for (_, p) in df.iterrows())

    def get_race_laps(self, df: DataFrame) -> int:
        return len(df.columns) - 4

    ####################################################
    #              DATAFRAME PROCESSING                #
    ####################################################

    def _clean_dataframe(self, df: DataFrame) -> DataFrame:
        # remove rows without any content
        remove = []
        for index, row in df.iterrows():
            col_with_content = 0
            for _, col in row.items():
                content = whitespaces_clean(col)
                if content and len(content) > 5:
                    col_with_content += 1
            if col_with_content < 3:  # check we at least have (maybe) name, final time and category
                remove.append(index)

        df.drop(remove, inplace=True)
        df.drop([0, len(df.columns) - 1], axis=1, inplace=True)

        df = df.map(lambda w: w[1:] if w.startswith("I") else w)  # some vertical lines are confused with I
        df[2] = df[2].apply(lambda w: whitespaces_clean("".join([c for c in w if c.isalpha()])))

        return df
