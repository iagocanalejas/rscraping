import logging
import requests

from ._client import Client
from typing import Optional
from parsel import Selector
from data.constants import HTTP_HEADERS
from data.models import Datasource, Lineup, Race
from parsers.html import ARCHtmlParser

logger = logging.getLogger(__name__)


class ARCClient(Client, source=Datasource.ARC):
    DATASOURCE = Datasource.ARC

    @staticmethod
    def get_url(race_id: str, is_female: bool, **_) -> str:
        host = "ligaete" if is_female else "liga-arc"
        return f"https://www.{host}.com/es/regata/{race_id}/unknown"

    @staticmethod
    def get_lineup_url(race_id: str, club_id: str, is_female: bool, **_) -> str:
        host = "ligaete" if is_female else "liga-arc"
        return f"http://www.{host}.com/es/regata/{race_id}/unknown/equipo/{club_id}/unknown"

    def get_race_by_id(self, race_id: str, is_female: bool, **_) -> Optional[Race]:
        url = self.get_url(race_id, is_female)
        race = ARCHtmlParser().parse_race(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).text),
            race_id=race_id,
            is_female=is_female,
        )
        if race:
            race.url = url
        return race

    def get_lineup_by_race_id(self, race_id: str, club_id: str, is_female: bool, **_) -> Lineup:
        url = self.get_lineup_url(race_id, club_id, is_female)
        return ARCHtmlParser().parse_lineup(selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).text))
