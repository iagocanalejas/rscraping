from typing import Any, Generator, Optional, override

import requests
from parsel import Selector

from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup, RaceName
from rscraping.parsers.html import TrainerasHtmlParser

from ._client import Client


class TrainerasClient(Client, source=Datasource.TRAINERAS):
    _html_parser: TrainerasHtmlParser

    DATASOURCE = Datasource.TRAINERAS
    MALE_START = FEMALE_START = 1960

    def __init__(self, **_) -> None:
        super().__init__()
        self._html_parser = TrainerasHtmlParser()

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
    @staticmethod
    def get_lineup_url(lineup_id: str, **_):
        return f"https://traineras.es/alineaciones/{lineup_id}"

    def get_pages(self, year: int) -> Generator[Selector, Any, Any]:
        def selector(year: int, page: int) -> Selector:
            return Selector(
                requests.get(url=self.get_races_url(year, page=page), headers=HTTP_HEADERS).content.decode("utf-8")
            )

        page = 1
        first_page = selector(year, page)
        while page <= self._html_parser.get_number_of_pages(first_page):
            yield (selector(year, page) if page != 1 else first_page)
            page += 1

    @override
    def get_race_ids_by_year(self, year: int, **_) -> Generator[str, Any, Any]:
        self.validate_year_or_raise_exception(year)
        for page in self.get_pages(year):
            yield from self._html_parser.parse_race_ids(page, is_female=self._is_female)

    def get_race_ids_by_rower(self, rower_id: str, year: Optional[str] = None, **_) -> Generator[str, Any, Any]:
        content = requests.get(url=self.get_rower_url(rower_id), headers=HTTP_HEADERS).content.decode("utf-8")
        yield from self._html_parser.parse_rower_race_ids(Selector(content), year=year)

    @override
    def get_race_names_by_year(self, year: int, **_) -> Generator[RaceName, Any, Any]:
        self.validate_year_or_raise_exception(year)
        for page in self.get_pages(year):
            yield from self._html_parser.parse_race_names(page)

    @override
    def get_lineup_by_race_id(self, race_id: str, **_) -> Generator[Lineup, Any, Any]:
        content = requests.get(url=self.get_race_details_url(race_id), headers=HTTP_HEADERS).content.decode("utf-8")
        participants = self._html_parser.get_participants(Selector(content), day=1)
        for participant in participants:
            url = participant.xpath("//*/td[9]/a/@href").get("")
            if not url:
                continue
            lineup = requests.get(url=url, headers=HTTP_HEADERS).content.decode("utf-8")
            yield self._html_parser.parse_lineup(Selector(lineup))
