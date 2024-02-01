from collections.abc import Generator
from datetime import date
from typing import Any, Protocol, override

import requests
from parsel.selector import Selector

from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup, Race, RaceName
from rscraping.parsers.html import HtmlParser
from rscraping.parsers.pdf import PdfParser


class ClientProtocol(Protocol):
    DATASOURCE: Datasource
    FEMALE_START: int
    MALE_START: int

    @property
    def _html_parser(self) -> HtmlParser: ...

    @property
    def _pdf_parser(self) -> PdfParser: ...

    def validate_year(self, year: int, is_female: bool):
        """
        Validate the given year for validity in datasource, raising a ValueError if it's outside the valid range.

        Args:
            year (int): The year to validate.
            is_female (bool): Flag indicating whether it's a female race.

        Raises: ValueError: If the year is outside the valid range.
        """
        ...

    def get_race_by_id(self, race_id: str, is_female: bool, **kwargs) -> Race | None:
        """
        Retrieve race details by ID, parsing data from the corresponding URL.

        Args:
            race_id (str): The ID of the race.
            is_female (bool): Flag indicating whether it's a female race.
            **kwargs: Additional keyword arguments.

        Returns: Race | None: The parsed race details or None if the race is not found.
        """
        ...

    def get_race_ids_by_year(self, year: int, is_female: bool | None = None, **kwargs) -> Generator[str, Any, Any]:
        """
        Find the race IDs for a given year and gender.

        Args:
            year (int): The year for which to generate race IDs.
            is_female (bool): Flag indicating whether it's a female race.
            **kwargs: Additional keyword arguments.

        Yields: str: Race IDs.
        """
        ...

    def get_race_names_by_year(
        self, year: int, is_female: bool | None = None, **kwargs
    ) -> Generator[RaceName, Any, Any]:
        """
        Find the race names for a given year and gender.

        Args:
            year (int): The year for which to generate race names.
            is_female (bool): Flag indicating whether it's a female race.
            **kwargs: Additional keyword arguments.

        Yields: RaceName: Race names.
        """
        ...

    def get_race_ids_by_rower(self, rower_id: str, **kwargs) -> Generator[str, Any, Any]:
        """
        Find the race IDs associated with a specific rower.

        Args:
            rower_id (str): The ID of the rower.
            **kwargs: Additional keyword arguments.

        Yields: str: Race IDs associated with the rower.
        """
        ...

    def get_lineup_by_race_id(self, race_id: str, **kwargs) -> Generator[Lineup, Any, Any]:
        """
        Get the lineups for a specific race.

        Args:
            race_id (str): The ID of the race.
            **kwargs: Additional keyword arguments.

        Yields: Lineup: Lineups for the race.
        """
        ...

    @staticmethod
    def get_race_details_url(race_id: str, **kwargs) -> str:
        """
        Return the URL for retrieving details of a specific race.
        """
        ...

    @staticmethod
    def get_races_url(year: int, **kwargs) -> str:
        """
        Return the URL for retrieving races in a specific year.
        """
        ...

    @staticmethod
    def get_lineup_url(race_id: str, **kwargs) -> str:
        """
        Return the URL for retrieving the lineup of a specific race.
        """
        ...


class Client(ClientProtocol):
    _registry = {}

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

    def __new__(cls, source: Datasource, **_) -> "Client":
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)

        return final_obj

    @override
    def validate_year(self, year: int, is_female: bool):
        since = self.FEMALE_START if is_female else self.MALE_START
        today = date.today().year
        if year < since or year > today:
            raise ValueError(f"invalid 'year', available values are [{since}, {today}]")

    @override
    def get_race_by_id(self, race_id: str, is_female: bool, **kwargs) -> Race | None:
        url = self.get_race_details_url(race_id, is_female=is_female)
        race = self._html_parser.parse_race(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8")),
            race_id=race_id,
            is_female=is_female,
            **kwargs,
        )
        if race:
            race.url = url
        return race

    @override
    def get_race_ids_by_year(self, year: int, is_female: bool | None = None, **kwargs) -> Generator[str, Any, Any]:
        self.validate_year(year, is_female=bool(is_female))

        url = self.get_races_url(year, is_female=bool(is_female))
        yield from self._html_parser.parse_race_ids(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS()).text),
            is_female=is_female,
            **kwargs,
        )

    @override
    def get_race_names_by_year(
        self, year: int, is_female: bool | None = None, **kwargs
    ) -> Generator[RaceName, Any, Any]:
        self.validate_year(year, is_female=bool(is_female))

        url = self.get_races_url(year, is_female=bool(is_female))
        yield from self._html_parser.parse_race_names(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8")),
            is_female=is_female,
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
