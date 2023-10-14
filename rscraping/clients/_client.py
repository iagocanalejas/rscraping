from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Generator, Optional

import requests
from parsel import Selector

from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup, Race, RaceName
from rscraping.parsers.html import HtmlParser
from rscraping.parsers.pdf import PdfParser


class Client(ABC):
    _registry = {}
    _is_female = False
    _html_parser: HtmlParser
    _pdf_parser: PdfParser

    DATASOURCE: Datasource
    FEMALE_START: int
    MALE_START: int

    def __init_subclass__(cls, **kwargs):
        source = kwargs.pop("source", None)
        super().__init_subclass__(**kwargs)
        if source:
            cls._registry[source] = cls

    def __new__(cls, source: Datasource, is_female: bool = False, **_) -> "Client":
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)
        final_obj._is_female = is_female

        return final_obj

    def validate_year_or_raise_exception(self, year: int):
        since = self.FEMALE_START if self._is_female else self.MALE_START
        today = date.today().year
        if year < since or year > today:
            raise ValueError(f"invalid 'year', available values are [{since}, {today}]")

    def get_race_by_id(self, race_id: str, **kwargs) -> Optional[Race]:
        url = self.get_race_details_url(race_id, is_female=self._is_female)
        race = self._html_parser.parse_race(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).content.decode("utf-8")),
            race_id=race_id,
            **kwargs,
        )
        if race:
            race.url = url
        return race

    def get_race_ids_by_year(self, year: int, **kwargs) -> Generator[str, Any, Any]:
        self.validate_year_or_raise_exception(year)

        url = self.get_races_url(year, is_female=self._is_female)
        yield from self._html_parser.parse_race_ids(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).text),
            **kwargs,
        )

    def get_race_names_by_year(self, year: int, **kwargs) -> Generator[RaceName, Any, Any]:
        self.validate_year_or_raise_exception(year)

        url = self.get_races_url(year, is_female=self._is_female)
        yield from self._html_parser.parse_race_names(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).content.decode("utf-8")),
            **kwargs,
        )

    ####################################################
    #                     ABSTRACT                     #
    ####################################################

    @staticmethod
    @abstractmethod
    def get_race_details_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_races_url(year: int, **kwargs) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_lineup_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_race_ids_by_rower(self, rower_id: str, **_) -> Generator[str, Any, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_lineup_by_race_id(self, race_id: str, **kwargs) -> Generator[Lineup, Any, Any]:
        raise NotImplementedError
