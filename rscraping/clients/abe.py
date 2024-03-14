from typing import override

from rscraping.data.models import Datasource
from rscraping.parsers.html import ABEHtmlParser

from ._client import Client


# TODO: web is down maybe new web
class ABEClient(Client, source=Datasource.ABE):
    DATASOURCE = Datasource.ABE
    MALE_START = FEMALE_START = 2023

    @property
    def _html_parser(self) -> ABEHtmlParser:
        return ABEHtmlParser()

    @override
    @staticmethod
    def get_race_details_url(race_id: str, **_) -> str:
        return f"https://lasalveliga.com/es/regata/{race_id}/"

    @override
    @staticmethod
    def get_races_url(year: int, **_) -> str:
        return f"https://lasalveliga.com/es/regatas-{year - 1}/"

    @override
    def validate_url(self, url: str):
        raise NotImplementedError
