from collections.abc import Callable, Generator
from datetime import date
from typing import Any, override

import pandas as pd

from pyutils.shortcuts import only_one_not_none
from pyutils.strings import roman_to_int
from rscraping.data.models import Datasource, Lineup, Race, RaceName
from rscraping.parsers.df import (
    COLUMN_CLUB,
    COLUMN_DATE,
    COLUMN_DISTANCE,
    COLUMN_EDITION,
    COLUMN_LANE,
    COLUMN_LEAGUE,
    COLUMN_NAME,
    COLUMN_NUMBER_LANES,
    COLUMN_NUMBER_LAPS,
    COLUMN_ORGANIZER,
    COLUMN_TIME,
    COLUMN_TYPE,
    GoogleDriveDataFrameParser,
)
from rscraping.parsers.html import HtmlParser
from rscraping.parsers.pdf import PdfParser

from ._client import ClientProtocol


class GoogleDriveClient(ClientProtocol):
    DATASOURCE = Datasource.GDRIVE
    FEMALE_START = 2015
    MALE_START = 2011

    _df_types: dict[Any, Callable] = {
        "N": lambda x: int(x) if x else None,
        COLUMN_CLUB: lambda x: str(x) if x else None,
        COLUMN_DATE: lambda x: pd.to_datetime(x, format="%d/%m/%Y").date() if x and x != "-" else None,
        COLUMN_LEAGUE: lambda x: str(x) if x and x != "-" else None,
        COLUMN_EDITION: lambda x: roman_to_int(x) if x and x != "-" else None,
        COLUMN_NAME: lambda x: str(x) if x else None,
        COLUMN_ORGANIZER: lambda x: str(x) if x else None,
        COLUMN_DISTANCE: lambda x: int(x) if x else None,
        COLUMN_TIME: lambda x: pd.to_datetime(x, format="%M:%S.%f").time() if x and x != "-" else None,
        COLUMN_TYPE: lambda x: str(x) if x else None,
        COLUMN_NUMBER_LAPS: lambda x: int(x) if x else None,
        COLUMN_NUMBER_LANES: lambda x: int(x) if x else None,
        COLUMN_LANE: lambda x: int(x) if x else None,
    }

    @property
    def _parser(self) -> GoogleDriveDataFrameParser:
        return GoogleDriveDataFrameParser()

    @override
    def validate_year(self, year: int, is_female: bool):
        since = self.FEMALE_START if is_female else self.MALE_START
        today = date.today().year
        if year < since or year > today:
            raise ValueError(f"invalid 'year', available values are [{since}, {today}]")

    @override
    @staticmethod
    def get_race_details_url(*_, sheet_id: str, sheet_name: str | None = None, **kwargs) -> str:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
        if sheet_name:
            url += f"&sheet={sheet_name}"
        return url

    @override
    def get_race_by_id(
        self,
        race_id: str,
        *_,
        sheet_id: str | None = None,
        file_path: str | None = None,
        sheet_name: str | None = None,
        is_female: bool = False,
        **kwargs,
    ) -> Race | None:
        if not only_one_not_none(sheet_id, file_path):
            raise ValueError("sheet_id and file_path are mutually exclusive")

        df = self._load_dataframe(sheet_id=sheet_id, file_path=file_path, sheet_name=sheet_name)
        race_row = df.iloc[int(race_id) - 1]

        return self._parser.parse_race_serie(race_row, is_female=is_female)

    def get_races(
        self,
        sheet_id: str | None = None,
        file_path: str | None = None,
        sheet_name: str | None = None,
        is_female: bool = False,
        **kwargs,
    ) -> Generator[Race, Any, Any]:
        if not only_one_not_none(sheet_id, file_path):
            raise ValueError("sheet_id and file_path are mutually exclusive")

        df = self._load_dataframe(sheet_id=sheet_id, file_path=file_path, sheet_name=sheet_name)
        return self._parser.parse_races_from(df, is_female=is_female)

    def _load_dataframe(
        self, sheet_id: str | None = None, file_path: str | None = None, sheet_name: str | None = None
    ) -> pd.DataFrame:
        df = None

        if sheet_id:
            url = self.get_race_details_url(sheet_id=sheet_id, sheet_name=sheet_name)
            df = pd.read_csv(url, header=0, index_col=0, converters=self._df_types).fillna("")

        if file_path:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path, header=0, index_col=0, converters=self._df_types).fillna("")
            if file_path.endswith(".xlsx"):
                df = pd.read_excel(file_path, header=0, index_col=0, converters=self._df_types).fillna("")

        assert isinstance(df, pd.DataFrame)

        # remove unused dataframe parts
        # 1. remove rows with NaN index
        # 2. keep only the first 15 columns
        # 3. remove columns "Temp." and "Puesto"
        # 4. remove rows with empty "Nome" column
        df = df[df.index.notnull()].iloc[:, :15].drop(columns=["Temp.", "Puesto"]).loc[df[COLUMN_NAME] != ""]

        return df

    ################################################
    ######## NOT IMPLEMENTED METHODS ###############
    ################################################

    @property
    def _html_parser(self) -> HtmlParser:
        raise NotImplementedError

    @property
    def _pdf_parser(self) -> PdfParser:
        raise NotImplementedError

    def get_race_ids_by_year(self, year: int, is_female: bool | None = None, **kwargs) -> Generator[str, Any, Any]:
        raise NotImplementedError

    def get_race_names_by_year(
        self, year: int, is_female: bool | None = None, **kwargs
    ) -> Generator[RaceName, Any, Any]:
        raise NotImplementedError

    def get_race_ids_by_rower(self, rower_id: str, **kwargs) -> Generator[str, Any, Any]:
        raise NotImplementedError

    def get_lineup_by_race_id(self, race_id: str, **kwargs) -> Generator[Lineup, Any, Any]:
        raise NotImplementedError

    @staticmethod
    def get_races_url(year: int, **kwargs) -> str:
        raise NotImplementedError

    @staticmethod
    def get_lineup_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError
