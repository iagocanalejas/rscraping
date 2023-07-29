from datetime import date
import logging
import requests

from ._client import Client
from typing import List, Optional
from parsel import Selector
from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup, Race
from rscraping.parsers.html import TrainerasHtmlParser


logger = logging.getLogger(__name__)


class TrainerasClient(Client, source=Datasource.TRAINERAS):
    DATASOURCE = Datasource.TRAINERAS
    MALE_START = FEMALE_START = 1960

    @staticmethod
    def get_race_details_url(race_id: str, **_) -> str:
        return f"https://traineras.es/clasificaciones/{race_id}"

    @staticmethod
    def get_races_url(year: int, page: int = 1, **_) -> str:
        return f"https://traineras.es/regatas/{year}?page={page}"

    @staticmethod
    def get_lineup_url(**_) -> str:
        raise NotImplementedError

    def get_race_by_id(self, race_id: str, day: Optional[int] = None, **_) -> Optional[Race]:
        url = self.get_race_details_url(race_id)
        race = TrainerasHtmlParser().parse_race(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).content.decode("utf-8")),
            race_id=race_id,
            day=day,
        )
        if race:
            race.url = url
        return race

    def get_race_ids_by_year(self, year: int, **_) -> List[str]:
        since = self.MALE_START
        today = date.today().year
        if year < since or year > today:
            raise ValueError(f"invalid 'year', available values are [{since}, {today}]")

        ids: List[str] = []
        parser: TrainerasHtmlParser = TrainerasHtmlParser()

        page = 1
        first_page = Selector(requests.get(url=self.get_races_url(year, page=page), headers=HTTP_HEADERS).text)
        while page <= parser.get_number_of_pages(first_page):
            selector = (
                Selector(requests.get(url=self.get_races_url(year, page=page), headers=HTTP_HEADERS).text)
                if page != 1
                else first_page
            )

            ids.extend(parser.parse_race_ids(selector))

            page += 1
        return ids

    def get_lineup_by_race_id(self, race_id: str, **_) -> List[Lineup]:
        raise NotImplementedError
