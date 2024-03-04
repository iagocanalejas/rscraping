from collections.abc import Generator
from typing import Any, override

import requests
from parsel.selector import Selector

from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup
from rscraping.parsers.html import ARCHtmlParser

from ._client import Client


class ARCClient(Client, source=Datasource.ARC):
    DATASOURCE = Datasource.ARC
    MALE_START = 2009
    FEMALE_START = 2018

    @property
    def _html_parser(self) -> ARCHtmlParser:
        return ARCHtmlParser()

    @override
    @staticmethod
    def get_race_details_url(race_id: str, *, is_female: bool, **_) -> str:
        host = "ligaete" if is_female else "liga-arc"
        return f"https://www.{host}.com/es/regata/{race_id}/unknown"

    @override
    @staticmethod
    def get_races_url(year: int, *, is_female: bool, **_) -> str:
        host = "ligaete" if is_female else "liga-arc"
        return f"https://www.{host}.com/es/calendario/{year}"

    @override
    @staticmethod
    def get_lineup_url(race_id: str, *, club_id: str, is_female: bool, **_) -> str:
        host = "ligaete" if is_female else "liga-arc"
        return f"http://www.{host}.com/es/regata/{race_id}/unknown/equipo/{club_id}/unknown"

    @override
    def get_lineup_by_race_id(self, race_id: str, **__) -> Generator[Lineup, Any, Any]:
        url = f"http://www.{'ligaete' if self._is_female else 'liga-arc'}.com/es/regata/{race_id}/unknown/equipos"
        selector = Selector(requests.get(url=url, headers=HTTP_HEADERS()).text)
        club_ids = self._html_parser.parse_club_ids(selector=selector)

        for club_id in club_ids:
            url = self.get_lineup_url(race_id, club_id=club_id, is_female=self._is_female)
            selector = Selector(requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8"))
            yield self._html_parser.parse_lineup(selector=selector)
