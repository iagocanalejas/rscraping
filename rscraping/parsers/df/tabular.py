from collections.abc import Generator
from typing import Any

from pandas import DataFrame, Series

from pyutils.strings import int_or_none
from rscraping.data.constants import (
    CATEGORY_ABSOLUT,
    GENDER_FEMALE,
    GENDER_MALE,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Datasource, Participant, Race
from rscraping.data.normalization import (
    extract_town,
    normalize_club_name,
    normalize_name_parts,
    normalize_race_name,
    remove_day_indicator,
)

from ._parser import DataFrameParserProtocol

COLUMN_CLUB = "Club"
COLUMN_ORGANIZER = "Organizador"
COLUMN_TYPE = "Tipo"
COLUMN_NAME = "Nome"
COLUMN_DATE = "Fecha"
COLUMN_LEAGUE = "Liga"
COLUMN_EDITION = "Edición"
COLUMN_DISTANCE = "Distancia"
COLUMN_TIME = "Tiempo"
COLUMN_LANE = "Boya"
COLUMN_NUMBER_LANES = "N Boyas"
COLUMN_NUMBER_LAPS = "N Largos"


class TabularDataFrameParser(DataFrameParserProtocol):
    def parse_race_serie(self, row: Series, is_female: bool = False, url: str | None = None) -> Race | None:
        if not isinstance(row, Series):
            return None

        normalized_names = normalize_name_parts(normalize_race_name(str(row[COLUMN_NAME])))
        if len(normalized_names) == 0:
            return None
        normalized_names = [(remove_day_indicator(n), e) for (n, e) in normalized_names]

        race = Race(
            name=str(row[COLUMN_NAME]),
            normalized_names=normalized_names,
            date=row[COLUMN_DATE].strftime("%d/%m/%Y"),  # pyright: ignore
            type=RACE_TIME_TRIAL if str(row[COLUMN_TYPE]) == "Contrarreloxo" else RACE_CONVENTIONAL,
            day=2 if "XORNADA" in row[COLUMN_NAME] and "2" in row[COLUMN_NAME] else 1,
            modality=RACE_TRAINERA,
            league=str(row[COLUMN_LEAGUE]).upper() if str(row[COLUMN_LEAGUE]) else None,
            town=extract_town(normalize_race_name(str(row[COLUMN_NAME]))),
            organizer=str(row[COLUMN_ORGANIZER]).upper() if str(row[COLUMN_ORGANIZER]) else None,
            sponsor=None,
            race_ids=[str(int(row.name))],  # pyright: ignore
            url=url,
            gender=GENDER_FEMALE if is_female else GENDER_MALE,
            datasource=Datasource.TABULAR.value,
            cancelled=False,
            race_laps=int_or_none(str(row[COLUMN_NUMBER_LAPS])),
            race_lanes=int_or_none(str(row[COLUMN_NUMBER_LANES])),
            participants=[],
        )

        race.participants = [
            Participant(
                gender=GENDER_FEMALE if is_female else GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name=str(row[COLUMN_CLUB]).upper(),
                lane=int_or_none(str(row[COLUMN_LANE])),
                series=None,
                laps=[row[COLUMN_TIME].strftime("%M:%S.%f")] if row[COLUMN_TIME] else [],  # pyright: ignore
                distance=int(str(row[COLUMN_DISTANCE])) if row[COLUMN_DISTANCE] else 5556,  # pyright: ignore
                handicap=None,
                participant=normalize_club_name(str(row[COLUMN_CLUB])),
                race=race,
                disqualified=False,
            )
        ]

        return race

    def parse_races_from(
        self,
        data: DataFrame,
        *_,
        is_female: bool = False,
        url: str | None = None,
        **__,
    ) -> Generator[Race, Any, Any]:
        for _, row in data.iterrows():
            race = self.parse_race_serie(row, is_female=is_female, url=url)
            if race:
                yield race
