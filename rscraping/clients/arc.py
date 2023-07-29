from datetime import date
import logging
import requests

from ._client import Client
from typing import List, Optional
from parsel import Selector
from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup, Race
from rscraping.parsers.html import ARCHtmlParser

logger = logging.getLogger(__name__)


class ARCClient(Client, source=Datasource.ARC):
    DATASOURCE = Datasource.ARC
    MALE_START = 2009
    FEMALE_START = 2018

    @staticmethod
    def get_race_details_url(race_id: str, is_female: bool, **_) -> str:
        host = "ligaete" if is_female else "liga-arc"
        return f"https://www.{host}.com/es/regata/{race_id}/unknown"

    @staticmethod
    def get_races_url(year: int, is_female: bool, **_) -> str:
        host = "ligaete" if is_female else "liga-arc"
        return f"https://www.{host}.com/es/calendario/{year}"

    @staticmethod
    def get_lineup_url(race_id: str, club_id: str, is_female: bool, **_) -> str:
        host = "ligaete" if is_female else "liga-arc"
        return f"http://www.{host}.com/es/regata/{race_id}/unknown/equipo/{club_id}/unknown"

    def get_race_by_id(self, race_id: str, **_) -> Optional[Race]:
        url = self.get_race_details_url(race_id, self._is_female)
        race = ARCHtmlParser().parse_race(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).content.decode("utf-8")),
            race_id=race_id,
            is_female=self._is_female,
        )
        if race:
            race.url = url
        return race

    def get_race_ids_by_year(self, year: int, **_) -> List[str]:
        since = self.FEMALE_START if self._is_female else self.MALE_START
        today = date.today().year
        if year < since or year > today:
            raise ValueError(f"invalid 'year', available values are [{since}, {today}]")

        url = self.get_races_url(year, self._is_female)
        return ARCHtmlParser().parse_race_ids(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).text),
        )

    def get_lineup_by_race_id(self, race_id: str, **_) -> List[Lineup]:
        parser = ARCHtmlParser()

        # find participants in race
        url = f"http://www.{'ligaete' if self._is_female else 'liga-arc'}.com/es/regata/{race_id}/unknown/equipos"
        club_ids = parser.parse_club_ids(selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).text))

        # get lineups
        lineups = []
        for club_id in club_ids:
            url = self.get_lineup_url(race_id, club_id, self._is_female)
            lineups.append(parser.parse_lineup(selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).text)))
        return lineups
