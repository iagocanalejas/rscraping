import requests
from ._client import Client
from typing import Any, Generator, List
from parsel import Selector
from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup, RaceName
from rscraping.parsers.html import TrainerasHtmlParser


class TrainerasClient(Client, source=Datasource.TRAINERAS):
    _html_parser: TrainerasHtmlParser

    DATASOURCE = Datasource.TRAINERAS
    MALE_START = FEMALE_START = 1960

    def __init__(self, **_) -> None:
        super().__init__()
        self._html_parser = TrainerasHtmlParser()

    @staticmethod
    def get_race_details_url(race_id: str, **_) -> str:
        return f"https://traineras.es/clasificaciones/{race_id}"

    @staticmethod
    def get_races_url(year: int, page: int = 1, **_) -> str:
        return f"https://traineras.es/regatas/{year}?page={page}"

    @staticmethod
    def get_lineup_url(**_) -> str:
        raise NotImplementedError

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

    def get_race_ids_by_year(self, year: int, **_) -> List[str]:
        self.validate_year_or_raise_exception(year)

        ids: List[str] = []
        for page in self.get_pages(year):
            ids.extend(self._html_parser.parse_race_ids(page))
        return ids

    def get_race_names_by_year(self, year: int, **_) -> List[RaceName]:
        self.validate_year_or_raise_exception(year)

        race_names: List[RaceName] = []
        for page in self.get_pages(year):
            race_names.extend(self._html_parser.parse_race_names(page))
        return race_names

    def get_lineup_by_race_id(self, **_) -> List[Lineup]:
        raise NotImplementedError
