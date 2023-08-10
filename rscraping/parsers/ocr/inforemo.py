import locale
import logging
from datetime import date, datetime
from typing import Any, Generator, List, Optional, Tuple

import inquirer
from pandas import DataFrame, Series

from pyutils.strings import find_date, remove_symbols, whitespaces_clean
from rscraping.data.constants import (
    GENDER_FEMALE,
    GENDER_MALE,
    GENDER_MIX,
    PARTICIPANT_CATEGORY_ABSOLUT,
    PARTICIPANT_CATEGORY_VETERAN,
    RACE_CONVENTIONAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Datasource, Participant, Race
from rscraping.data.normalization.clubs import normalize_club_name
from rscraping.data.normalization.races import normalize_name_parts, normalize_race_name
from rscraping.data.normalization.times import normalize_lap_time, normalize_spanish_months

from ._parser import OcrParser

logger = logging.getLogger(__name__)


class InforemoOcrParser(OcrParser, source=Datasource.INFOREMO):
    DATASOURCE = Datasource.INFOREMO

    _GENDERS = {
        GENDER_MALE: ["MASCULINO", "ABSOLUTO", "VETERANO"],
        GENDER_FEMALE: ["FEMENINO", "VETERANA"],
        GENDER_MIX: ["MIXTO"],
    }

    def parse_races_from(
        self,
        file_name: str,
        header: str,
        tabular: DataFrame,
        language: str = "es_ES.utf8",
        manual_input: bool = False,
        **_,
    ) -> Generator[Race, Any, Any]:
        locale.setlocale(locale.LC_TIME, language)

        name, t_date = self._parse_header_data(header, manual_input=manual_input)
        if not name:
            raise ValueError(f"{self.DATASOURCE}: no name found")
        if not t_date:
            raise ValueError(f"{self.DATASOURCE}: no date found")

        df = self._clean_dataframe(tabular)

        race_lanes = self.get_race_lanes(df)
        race_laps = self.get_race_laps(df)

        identifiers = df[2].unique()
        for identifier in identifiers:
            participants: DataFrame = df[df[2] == identifier]

            genders = [self.get_gender(p) for (_, p) in participants.iterrows()]
            gender = (
                genders[0]
                if all(g == genders[0] for g in genders) and genders[0] in [GENDER_MALE, GENDER_FEMALE, GENDER_MIX]
                else None
            )

            # TODO: try to find hardcoded values
            race = Race(
                name=name,
                normalized_names=normalize_name_parts(name),
                date=t_date.strftime("%d/%m/%Y"),
                type=RACE_CONVENTIONAL,
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

            for _, participant in participants.iterrows():
                race.participants.append(
                    Participant(
                        gender=self.get_gender(participant),
                        category=self.get_category(participant),
                        club_name=self.get_club_name(participant),
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

            yield race

    def _parse_header_data(self, data: str, manual_input: bool) -> Tuple[Optional[str], Optional[date]]:
        name = t_date = None
        for part in data.split("\n"):
            if not name and part and not any(w in part for w in ["@", "inforemo"]):
                name = normalize_race_name(part)
                continue

            if not t_date:
                phrase = remove_symbols(normalize_spanish_months(part))
                t_date = find_date(phrase)

            if name and t_date:
                break

        if not name and manual_input:
            name = inquirer.text(message=f"no name found \n {data} \n set manual name for the race:")
        if not t_date and manual_input:
            t_date = inquirer.text(message=f"no date found \n {data} \n set manual date for race {name} (DD-MM-YYYY):")
            t_date = datetime.strptime("%d-%m-%Y", t_date).date() if t_date else None

        return (name, t_date)

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

    def get_series(self, data: Series) -> Optional[int]:
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

    def get_laps(self, data: Series) -> List[str]:
        idx = 3 if ":" in data[4] else 4
        return [t.isoformat() for t in [normalize_lap_time(self.clean_lap(t)) for t in data.iloc[idx:]] if t]

    def get_gender(self, data: Series) -> str:
        gender = str(data[2])
        for k, v in self._GENDERS.items():
            if gender in v or any(part in gender for part in v):
                return k
        return gender

    def get_category(self, data: Series) -> str:
        modality = data[2]
        if any(e in modality for e in ["VETERANO", "VETERANA"]):
            return PARTICIPANT_CATEGORY_VETERAN
        return PARTICIPANT_CATEGORY_ABSOLUT

    def get_race_lanes(self, df: DataFrame) -> int:
        rows = [str(row[4]) for (_, row) in df.iterrows()]
        lanes = max(int(row) for row in rows if row.isdigit())
        return lanes if lanes < 7 else 1

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
            if col_with_content < 2:  # check we at least have (maybe) name and final time
                remove.append(index)

        df.drop(remove, inplace=True)
        df.drop([0, len(df.columns) - 1], axis=1, inplace=True)

        return df
