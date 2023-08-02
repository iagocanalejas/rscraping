from ._client import Client
from typing import List
from rscraping.data.models import Datasource, Lineup
from rscraping.parsers.html import ABEHtmlParser


class ABEClient(Client, source=Datasource.ABE):
    _html_parser: ABEHtmlParser

    DATASOURCE = Datasource.ABE
    MALE_START = FEMALE_START = 2023

    def __init__(self, **_) -> None:
        super().__init__()
        self._html_parser = ABEHtmlParser()

    @staticmethod
    def get_race_details_url(race_id: str, **_) -> str:
        return f"https://lasalveliga.com/es/regata/{race_id}/"

    @staticmethod
    def get_races_url(year: int, **_) -> str:
        return f"https://lasalveliga.com/es/regatas-{year - 1}/"

    @staticmethod
    def get_lineup_url(**_) -> str:
        raise NotImplementedError

    def get_lineup_by_race_id(self, **_) -> List[Lineup]:
        raise NotImplementedError
