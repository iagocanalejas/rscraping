from collections.abc import Generator
from datetime import date
from typing import Any, override

import requests
from parsel.selector import Selector

from rscraping.data.constants import GENDER_FEMALE, GENDER_MALE, HTTP_HEADERS
from rscraping.data.models import Datasource, Race, RaceName
from rscraping.parsers.html import HtmlParser

from ._protocol import ClientProtocol


class Client(ClientProtocol):
    _registry = {}
    _gender: str = GENDER_MALE

    DATASOURCE: Datasource
    FEMALE_START: int
    MALE_START: int

    @property
    @override
    def _html_parser(self) -> HtmlParser:
        raise NotImplementedError

    @override
    def _is_valid_gender(self, gender: str) -> bool:
        return gender in [GENDER_MALE, GENDER_FEMALE]

    @property
    def is_female(self) -> bool:
        return self._gender == GENDER_FEMALE

    def __init_subclass__(cls, **kwargs):
        source = kwargs.pop("source", None)
        super().__init_subclass__(**kwargs)
        if source:
            cls._registry[source] = cls

    def __new__(cls, source: Datasource, gender: str = GENDER_MALE, **_) -> "Client":
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)
        if not final_obj._is_valid_gender(gender):
            raise ValueError(f"invalid {gender}")
        final_obj._gender = gender
        return final_obj

    @override
    def validate_year(self, year: int):
        since = self.FEMALE_START if self.is_female else self.MALE_START
        today = date.today().year
        if year < since or year > today:
            raise ValueError(f"invalid 'year', available values are [{since}, {today}]")

    @override
    def get_race_by_id(self, race_id: str, **kwargs) -> Race | None:
        url = self.get_race_details_url(race_id, is_female=self.is_female)
        return self.get_race_by_url(url, race_id=race_id, **kwargs)

    @override
    def get_race_by_url(self, url: str, race_id: str, **kwargs) -> Race | None:
        self.validate_url(url)
        race = self._html_parser.parse_race(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8")),
            race_id=race_id,
            is_female=self.is_female,
            **kwargs,
        )
        if race:
            race.url = url
        return race

    @override
    def get_race_ids_by_year(self, year: int, **kwargs) -> Generator[str, Any, Any]:
        self.validate_year(year)

        url = self.get_races_url(year, is_female=self.is_female)
        yield from self._html_parser.parse_race_ids(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS()).text),
            is_female=self.is_female,
            **kwargs,
        )

    @override
    def get_race_names_by_year(self, year: int, **kwargs) -> Generator[RaceName, Any, Any]:
        self.validate_year(year)

        url = self.get_races_url(year, is_female=self.is_female)
        yield from self._html_parser.parse_race_names(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8")),
            is_female=self.is_female,
            **kwargs,
        )

    ####################################################
    #                     ABSTRACT                     #
    ####################################################

    @override
    def validate_url(self, url: str):
        raise NotImplementedError

    @override
    @staticmethod
    def get_races_url(year: int, **kwargs) -> str:
        raise NotImplementedError

    @override
    @staticmethod
    def get_race_details_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError

    @override
    def get_race_ids_by_club(self, club_id: str, year: int, **kwargs) -> Generator[str, Any, Any]:
        raise NotImplementedError
