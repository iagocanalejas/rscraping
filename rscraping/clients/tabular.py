import re
from collections.abc import Callable, Generator
from dataclasses import dataclass
from datetime import date
from typing import Any, override

import pandas as pd

from pyutils.shortcuts import only_one_not_none
from pyutils.strings import roman_to_int
from rscraping.data.functions import is_female
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
    TabularDataFrameParser,
)
from rscraping.parsers.html import HtmlParser
from rscraping.parsers.pdf import PdfParser

from ._client import Client


@dataclass
class TabularClientConfig:
    file_path: str | None = None
    sheet_id: str | None = None
    sheet_name: str | None = None
    sheet_url: str | None = None


class TabularDataClient(Client, source=Datasource.TABULAR):
    DATASOURCE = Datasource.TABULAR
    FEMALE_START = 2015
    MALE_START = 2011

    config: TabularClientConfig

    _url: str | None = None
    _df: pd.DataFrame
    _df_types: dict[Any, Callable] = {
        "N": lambda x: str(x) if x else None,
        COLUMN_CLUB: lambda x: str(x) if x else None,
        COLUMN_DATE: lambda x: pd.to_datetime(x, format="%d/%m/%Y") if x and x != "-" else None,
        COLUMN_LEAGUE: lambda x: str(x) if x and x != "-" else None,
        COLUMN_EDITION: lambda x: str(roman_to_int(x)) if x and x != "-" else None,
        COLUMN_NAME: lambda x: str(x) if x else None,
        COLUMN_ORGANIZER: lambda x: str(x) if x else None,
        COLUMN_DISTANCE: lambda x: str(x) if x else None,  # HACK: required str cast to avoid ".0" suffix
        COLUMN_TIME: lambda x: pd.to_datetime(x, format="%M:%S.%f").time() if x and x != "-" else None,
        COLUMN_TYPE: lambda x: str(x) if x else None,
        COLUMN_NUMBER_LAPS: lambda x: str(x) if x else None,
        COLUMN_NUMBER_LANES: lambda x: str(x) if x else None,
        COLUMN_LANE: lambda x: str(x) if x else None,
    }

    @property
    def _parser(self) -> TabularDataFrameParser:
        return TabularDataFrameParser()

    @override
    @staticmethod
    def get_race_details_url(*_, sheet_id: str, sheet_name: str | None = None, **kwargs) -> str:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
        if sheet_name:
            url += f"&sheet={sheet_name.replace(' ', '+')}"
        return url

    def __init__(self, *_, config: TabularClientConfig, **kwargs) -> None:
        if not only_one_not_none(config.file_path, config.sheet_id, config.sheet_url):
            raise ValueError("sheet_id, sheet_url and file_path are mutually exclusive")
        self._df = self._load_dataframe(config)
        self.config = config

        if config.sheet_name and is_female(config.sheet_name.upper()):
            self._is_female = True

        super().__init__(**kwargs)

    @override
    def validate_year(self, year: int):
        since = self.FEMALE_START if self._is_female else self.MALE_START
        today = date.today().year
        if year < since or year > today:
            raise ValueError(f"invalid 'year', available values are [{since}, {today}]")

    @override
    def validate_url(self, url: str):
        pattern = re.compile(
            r"^(https?:\/\/)?"  # Scheme (http, https, or empty)
            r"(docs\.google\.com\/spreadsheets\/d\/)"  # Domain name
            r"([A-Za-z0-9-_]+)"  # Sheet ID
            r"(\/gviz\/tq\?tqx=out:csv)"  # Rest of the URL
            r"(&sheet=[A-Za-z0-9-_+]+)?$",  # race ID
            re.IGNORECASE,
        )

        if not pattern.match(url):
            raise ValueError(f"invalid {url=}")

    def get_races(self, **kwargs) -> Generator[Race, Any, Any]:
        """
        Retrieve all the race details in the current DataFrame.

        Yields: Race: All the races in the DataFrame.
        """
        return self._parser.parse_races(self._df, is_female=self._is_female, url=self._url)

    @override
    def get_race_by_id(self, race_id: str, *_, **kwargs) -> Race | None:
        race_row = self._df.iloc[int(race_id) - 1]
        return self._parser.parse_race(race_row, is_female=self._is_female, url=self._url)

    @override
    def get_race_by_url(self, *_, race_id: str, **kwargs) -> Race | None:
        return self.get_race_by_id(race_id=race_id, **kwargs)

    @override
    def get_race_names_by_year(self, year: int, *_, **kwargs) -> Generator[RaceName, Any, Any]:
        return self._parser.parse_race_names(self._df, year)

    @override
    def get_race_ids_by_year(self, year: int, *_, **kwargs) -> Generator[str, Any, Any]:
        return self._parser.parse_race_ids(self._df, year)

    ################################################
    ############## PRIVATE METHODS #################
    ################################################

    def _load_dataframe(self, config: TabularClientConfig) -> pd.DataFrame:
        df = None

        if config.sheet_url:
            self.validate_url(config.sheet_url)
            self._url = config.sheet_url
            df = pd.read_csv(self._url, header=0, index_col=0, converters=self._df_types).fillna("")

        if config.sheet_id:
            self._url = self.get_race_details_url(sheet_id=config.sheet_id, sheet_name=config.sheet_name)
            df = pd.read_csv(self._url, header=0, index_col=0, converters=self._df_types).fillna("")

        if config.file_path:
            if config.file_path.endswith(".csv"):
                df = pd.read_csv(config.file_path, header=0, index_col=0, converters=self._df_types).fillna("")
            if config.file_path.endswith(".xlsx"):
                df = pd.read_excel(config.file_path, header=0, index_col=0, converters=self._df_types).fillna("")

        assert isinstance(df, pd.DataFrame)

        # remove unused dataframe parts
        # 1. remove rows with NaN index
        # 2. keep only the first 15 columns
        # 3. remove column "Puesto"
        # 4. remove rows with empty "Nome" column
        df = df[df.index.notnull()].iloc[:, :15].drop(columns=["Puesto"]).loc[df[COLUMN_NAME] != ""]

        return df

    ################################################
    ######## NOT IMPLEMENTED METHODS ###############
    ################################################

    @property
    @override
    def _html_parser(self) -> HtmlParser:
        raise NotImplementedError

    @property
    @override
    def _pdf_parser(self) -> PdfParser:
        raise NotImplementedError

    @override
    def get_lineup_by_race_id(self, race_id: str, **kwargs) -> Generator[Lineup, Any, Any]:
        raise NotImplementedError

    @override
    @staticmethod
    def get_races_url(year: int, **kwargs) -> str:
        raise NotImplementedError

    @override
    @staticmethod
    def get_lineup_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError
