import re
from collections.abc import Generator
from typing import Any, override

import requests
from parsel.selector import Selector

from rscraping.data.constants import (
    CATEGORY_ABSOLUT,
    CATEGORY_SCHOOL,
    CATEGORY_VETERAN,
    GENDER_FEMALE,
    GENDER_MALE,
    GENDER_MIX,
    HTTP_HEADERS,
)
from rscraping.data.models import Datasource, Race, RaceName
from rscraping.parsers.html import TrainerasHtmlParser

from ._client import Client


class TrainerasClient(Client, source=Datasource.TRAINERAS):
    DATASOURCE = Datasource.TRAINERAS
    MALE_START = FEMALE_START = 1960

    _category: str = CATEGORY_ABSOLUT

    def __init__(self, category: str = CATEGORY_ABSOLUT, **kwargs) -> None:
        self._category = category
        super().__init__(**kwargs)

    @property
    @override
    def _html_parser(self) -> TrainerasHtmlParser:
        return TrainerasHtmlParser()

    @override
    def _is_valid_gender(self, gender: str) -> bool:
        return gender in [GENDER_MALE, GENDER_FEMALE, GENDER_MIX]

    @override
    @staticmethod
    def get_race_details_url(race_id: str, **_) -> str:
        return f"https://traineras.es/clasificaciones/{race_id}"

    @override
    @staticmethod
    def get_races_url(year: int, page: int = 1, **_) -> str:
        return f"https://traineras.es/regatas/{year}?page={page}"

    @staticmethod
    def get_search_races_url(name: str) -> str:
        return f"https://traineras.es/banderas?nombre={name.replace(' ', '+')}"

    @staticmethod
    def get_flag_url(flag_id: str) -> str:
        return f"https://traineras.es/banderas/{flag_id}"

    @staticmethod
    def get_rower_url(rower_id: str, **_) -> str:
        return f"https://traineras.es/personas/{rower_id}"

    def get_club_races_url(self, club_id: str, year: int, **_) -> str:
        param = f"?anyo={year}"
        if self._category == CATEGORY_VETERAN:
            extra = "VF" if self.is_female else "VM"
        elif self._category == CATEGORY_SCHOOL:
            extra = "JF" if self.is_female else "JM"
        else:
            extra = "SF" if self.is_female else "SM"
        param = f"{param}-{extra}"
        return f"https://traineras.es/clubregatas/{club_id}{param}"

    @override
    def validate_url(self, url: str):
        pattern = re.compile(
            r"^(https?:\/\/)?"  # Scheme (http, https, or empty)
            r"(traineras\.es\/clasificaciones\/)"  # Domain name
            r"([\d]*\/?)$",  # race ID
            re.IGNORECASE,
        )

        if not pattern.match(url):
            raise ValueError(f"invalid {url=}")

    def get_race_ids_by_flag(self, flag_id: str) -> Generator[str, Any, Any]:
        """
        Find the IDs of the race editions for a given flag.

        Args:
            flag_id (str): The ID of the flag.
            **kwargs: Additional keyword arguments.

        Yields: str: Race IDs.
        """
        url = self.get_flag_url(flag_id)
        content = Selector(requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8"))
        yield from self._html_parser.parse_flag_race_ids(content, gender=self._gender, category=self._category)

    @override
    def get_race_by_id(self, race_id: str, **kwargs) -> Race | None:
        """
        Retrieve race details by ID parsing data from 'traineras.es'.
        This method also retrieves the flag edition for the race if available.

        Args:
            race_id (str): The ID of the race.
            **kwargs: Additional keyword arguments.

        Returns: Race | None: The parsed race details or None if the race is not found.
        """
        race = super().get_race_by_id(race_id, **kwargs)
        if not race:
            return None

        # search the race name in the flags seach page
        url = self.get_search_races_url(race.name)
        content = Selector(requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8"))
        flag_urls = self._html_parser.parse_searched_flag_urls(content)

        if len(flag_urls) < 1:
            return race

        # the first flag should be an exact match of the given one, so we can use it to get the editions
        content = Selector(requests.get(url=flag_urls[0], headers=HTTP_HEADERS()).content.decode("utf-8"))
        editions = self._html_parser.parse_flag_editions(content, gender=self._gender, category=self._category)
        edition = next((e for (y, e) in editions if y == race.year), None)
        if edition:
            race.normalized_names = [(n[0], edition) for n in race.normalized_names]

        return race

    @override
    def get_race_names_by_year(self, year: int, **_) -> Generator[RaceName, Any, Any]:
        self.validate_year(year)
        for page in self.get_pages(year):
            yield from self._html_parser.parse_race_names(page, gender=self._gender, category=self._category)

    @override
    def get_race_ids_by_year(self, year: int, **_) -> Generator[str, Any, Any]:
        self.validate_year(year)
        for page in self.get_pages(year):
            yield from self._html_parser.parse_race_ids(page, gender=self._gender, category=self._category)

    @override
    def get_race_ids_by_club(self, club_id: str, year: int, **kwargs) -> Generator[str, Any, Any]:
        content = requests.get(url=self.get_club_races_url(club_id, year), headers=HTTP_HEADERS())
        content = content.content.decode("utf-8")
        return self._html_parser.parse_club_race_ids(Selector(content))

    def get_race_ids_by_rower(self, rower_id: str, year: str | None = None, **_) -> Generator[str, Any, Any]:
        """
        Find the race IDs associated with a specific rower.

        Args:
            rower_id (str): The ID of the rower.
            **kwargs: Additional keyword arguments.

        Yields: str: Race IDs associated with the rower.
        """
        content = requests.get(url=self.get_rower_url(rower_id), headers=HTTP_HEADERS()).content.decode("utf-8")
        yield from self._html_parser.parse_rower_race_ids(Selector(content), year=year)

    def get_pages(self, year: int) -> Generator[Selector, Any, Any]:
        """
        Generate Selector objects for each page of races in a specific year.

        Args:
            year (int): The year for which to generate race pages.

        Yields: Selector: Selector objects for each page.
        """

        def get_page_selector(page: int) -> Selector:
            url = self.get_races_url(year, page=page)
            content = requests.get(url, headers=HTTP_HEADERS()).content.decode("utf-8")
            return Selector(content)

        first_page = get_page_selector(1)
        total_pages = self._html_parser.get_number_of_pages(first_page)
        for page_number in range(2, total_pages + 1):
            yield get_page_selector(page_number)
