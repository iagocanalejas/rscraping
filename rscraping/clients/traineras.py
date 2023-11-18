from collections.abc import Generator
from typing import Any, override

import requests
from parsel import Selector

from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup, RaceName
from rscraping.parsers.html import TrainerasHtmlParser

from ._client import Client


class TrainerasClient(Client, source=Datasource.TRAINERAS):
    DATASOURCE = Datasource.TRAINERAS
    MALE_START = FEMALE_START = 1960

    @property
    def _html_parser(self) -> TrainerasHtmlParser:
        return TrainerasHtmlParser()

    @override
    @staticmethod
    def get_race_details_url(race_id: str, **_) -> str:
        return f"https://traineras.es/clasificaciones/{race_id}"

    @override
    @staticmethod
    def get_races_url(year: int, page: int = 1, **_) -> str:
        return f"https://traineras.es/regatas/{year}?page={page}"

    @staticmethod
    def get_rower_url(rower_id: str, **_) -> str:
        return f"https://traineras.es/personas/{rower_id}"

    @override
    def get_race_ids_by_year(
        self, year: int, is_female: bool, *, category: str | None, **_
    ) -> Generator[str, Any, Any]:
        self.validate_year(year, is_female=is_female)
        for page in self.get_pages(year):
            yield from self._html_parser.parse_race_ids(page, is_female=is_female, category=category)

    @override
    def get_race_ids_by_rower(self, rower_id: str, year: str | None = None, **_) -> Generator[str, Any, Any]:
        content = requests.get(url=self.get_rower_url(rower_id), headers=HTTP_HEADERS()).content.decode("utf-8")
        yield from self._html_parser.parse_rower_race_ids(Selector(content), year=year)

    @override
    def get_race_names_by_year(
        self, year: int, is_female: bool, *, category: str | None, **_
    ) -> Generator[RaceName, Any, Any]:
        self.validate_year(year, is_female=is_female)
        for page in self.get_pages(year):
            yield from self._html_parser.parse_race_names(page, is_female=is_female, category=category)

    @override
    def get_lineup_by_race_id(self, race_id: str, **_) -> Generator[Lineup, Any, Any]:
        content = requests.get(url=self.get_race_details_url(race_id), headers=HTTP_HEADERS()).content.decode("utf-8")
        participants = self._html_parser.get_participants(Selector(content), day=1)
        for participant in participants:
            url = participant.xpath("//*/td[9]/a/@href").get("")
            if not url:
                continue
            lineup = requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8")
            yield self._html_parser.parse_lineup(Selector(lineup))

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
