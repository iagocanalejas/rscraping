import re
from typing import override

from rscraping.data.models import Datasource
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
    def get_race_details_url(self, race_id: str, *, is_female: bool, **_) -> str:
        host = "ligaete" if is_female else "liga-arc"
        return f"https://www.{host}.com/es/regata/{race_id}/unknown"

    @override
    def get_races_url(self, year: int, *, is_female: bool, **_) -> str:
        host = "ligaete" if is_female else "liga-arc"
        return f"https://www.{host}.com/es/calendario/{year}"

    @override
    def validate_url(self, url: str):
        pattern = re.compile(
            r"^(https?:\/\/)?"  # Scheme (http, https, or empty)
            r"(www\.(ligaete|liga-arc)\.com\/es\/regata\/)"  # Domain name
            r"([\d]*\/)"  # race ID
            r"(.*)$",  # rest of the shit the ARC uses
            flags=re.IGNORECASE,
        )

        if not pattern.match(url):
            raise ValueError(f"invalid {url=}")
