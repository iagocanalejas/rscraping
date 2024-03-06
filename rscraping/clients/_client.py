from collections.abc import Generator
from datetime import date
from typing import Any, override

import requests
from parsel.selector import Selector

from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup, Race, RaceName
from rscraping.parsers.html import HtmlParser
from rscraping.parsers.pdf import PdfParser

from ._protocol import ClientProtocol


class Client(ClientProtocol):
    _registry = {}
    _is_female: bool = False

    DATASOURCE: Datasource
    FEMALE_START: int
    MALE_START: int

    @property
    @override
    def _html_parser(self) -> HtmlParser:
        raise NotImplementedError

    @property
    @override
    def _pdf_parser(self) -> PdfParser:
        raise NotImplementedError

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

    @override
    def validate_year(self, year: int):
        since = self.FEMALE_START if self._is_female else self.MALE_START
        today = date.today().year
        if year < since or year > today:
            raise ValueError(f"invalid 'year', available values are [{since}, {today}]")

    @override
    def get_race_by_id(self, race_id: str, **kwargs) -> Race | None:
        url = self.get_race_details_url(race_id, is_female=self._is_female)
        race = self._html_parser.parse_race(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8")),
            race_id=race_id,
            is_female=self._is_female,
            **kwargs,
        )
        if race:
            race.url = url
        return race

    @override
    def get_race_ids_by_year(self, year: int, **kwargs) -> Generator[str, Any, Any]:
        self.validate_year(year)

        url = self.get_races_url(year, is_female=self._is_female)
        yield from self._html_parser.parse_race_ids(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS()).text),
            is_female=self._is_female,
            **kwargs,
        )

    @override
    def get_race_names_by_year(self, year: int, **kwargs) -> Generator[RaceName, Any, Any]:
        self.validate_year(year)

        url = self.get_races_url(year, is_female=self._is_female)
        yield from self._html_parser.parse_race_names(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8")),
            is_female=self._is_female,
            **kwargs,
        )

    ####################################################
    #                     ABSTRACT                     #
    ####################################################

    @override
    @staticmethod
    def get_race_details_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError

    @override
    @staticmethod
    def get_races_url(year: int, **kwargs) -> str:
        raise NotImplementedError

    @override
    @staticmethod
    def get_lineup_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError

    @override
    def get_race_ids_by_rower(self, rower_id: str, **kwargs) -> Generator[str, Any, Any]:
        raise NotImplementedError

    @override
    def get_lineup_by_race_id(self, race_id: str, **kwargs) -> Generator[Lineup, Any, Any]:
        raise NotImplementedError
