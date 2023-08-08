from typing import List

import requests
from parsel import Selector

from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup
from rscraping.parsers.html import ARCHtmlParser

from ._client import Client


class ARCClient(Client, source=Datasource.ARC):
    _html_parser: ARCHtmlParser

    DATASOURCE = Datasource.ARC
    MALE_START = 2009
    FEMALE_START = 2018

    def __init__(self, **_) -> None:
        super().__init__()
        self._html_parser = ARCHtmlParser()

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

    def get_lineup_by_race_id(self, race_id: str, **_) -> List[Lineup]:
        # find participants in race
        url = f"http://www.{'ligaete' if self._is_female else 'liga-arc'}.com/es/regata/{race_id}/unknown/equipos"
        club_ids = self._html_parser.parse_club_ids(selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).text))

        # get lineups
        lineups = []
        for club_id in club_ids:
            url = self.get_lineup_url(race_id, club_id, self._is_female)
            lineups.append(
                self._html_parser.parse_lineup(
                    selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).content.decode("utf-8"))
                )
            )
        return lineups
