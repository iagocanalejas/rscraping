from collections.abc import Generator
from datetime import date
from typing import override

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
from rscraping.data.models import Datasource, Participant, Race, RaceName
from rscraping.data.normalization import (
    extract_town,
    find_race_sponsor,
    normalize_club_name,
    normalize_name_parts,
    normalize_race_name,
    normalize_town,
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
    @override
    def parse_races(
        self,
        data: DataFrame,
        is_female: bool = False,
        url: str | None = None,
        **__,
    ) -> Generator[Race]:
        for _, row in data.iterrows():
            race = self.parse_race(row, is_female=is_female, url=url)
            if race:
                yield race

    def parse_race(self, row: Series, is_female: bool = False, url: str | None = None) -> Race | None:
        normalized_name = self._normalize_race_name(
            normalize_race_name(str(row[COLUMN_NAME])),
            str(row[COLUMN_LEAGUE]).upper() if str(row[COLUMN_LEAGUE]) else None,
            row[COLUMN_DATE],  # pyright: ignore
        )
        normalized_names = [
            (remove_day_indicator(n), int_or_none(str(row[COLUMN_EDITION])))
            for (n, _) in normalize_name_parts(normalized_name)
        ]
        if len(normalized_names) == 0:
            return None

        town = extract_town(normalized_name)

        race = Race(
            name=str(row[COLUMN_NAME]),
            normalized_names=normalized_names,
            date=row[COLUMN_DATE].strftime("%d/%m/%Y"),  # pyright: ignore
            type=RACE_TIME_TRIAL if str(row[COLUMN_TYPE]) == "Contrarreloxo" else RACE_CONVENTIONAL,
            day=2 if "XORNADA" in row[COLUMN_NAME] and "2" in row[COLUMN_NAME] else 1,
            modality=RACE_TRAINERA,
            league=str(row[COLUMN_LEAGUE]).upper() if str(row[COLUMN_LEAGUE]) else None,
            town=normalize_town(town) if town else None,
            organizer=str(row[COLUMN_ORGANIZER]).upper() if str(row[COLUMN_ORGANIZER]) else None,
            sponsor=find_race_sponsor(str(row[COLUMN_NAME])),
            race_ids=[row.name],  # pyright: ignore
            url=url,
            gender=GENDER_FEMALE if is_female else GENDER_MALE,
            category=CATEGORY_ABSOLUT,
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
                absent=False,
                retired=False,
            )
        ]

        return race

    def parse_race_ids(self, data: DataFrame, year: int) -> Generator[str]:
        df = data[data[COLUMN_DATE].dt.year == year]
        return (str(row.name) for _, row in df.iterrows())

    def parse_race_names(self, data: DataFrame, year: int) -> Generator[RaceName]:
        df = data[data[COLUMN_DATE].dt.year == year]
        return (RaceName(race_id=str(row.name), name=str(row[COLUMN_NAME])) for _, row in df.iterrows())

    @staticmethod
    def _normalize_race_name(name: str, league: str | None, t_date: date) -> str:
        if all(n in name for n in ["ILLA", "SAMERTOLAMEU"]) and (
            (league == "LIGA A" and t_date.year in [2023]) or (league == "LIGA B" and t_date.year in [2021, 2022])
        ):
            # HACK: this is a weird flag case in witch Meira restarted the edition for his 'B' team.
            return "BANDERA ILLA DO SAMERTOLAMEU - FANDICOSTA"

        return name
