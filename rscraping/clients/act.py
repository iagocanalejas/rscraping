import re
from typing import override

from rscraping.data.models import Datasource
from rscraping.parsers.html import ACTHtmlParser

from ._client import Client


class ACTClient(Client, source=Datasource.ACT):
    DATASOURCE = Datasource.ACT
    MALE_START = 2003
    FEMALE_START = 2009

    @property
    def _html_parser(self) -> ACTHtmlParser:
        return ACTHtmlParser()

    @override
    def get_race_details_url(self, race_id: str, *, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/ver.php?r={race_id}"

    @override
    def get_races_url(self, year: int, *, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/index.php?t={year}"

    @override
    def validate_url(self, url: str):
        pattern = re.compile(
            r"^(https?:\/\/)?"  # Scheme (http, https, or empty)
            r"(www\.euskolabelliga\.com)"  # Domain name
            r"(\/femenina)?"  # Optional female
            r"(\/resultados\/ver\.php\?r=)"  # Path
            r"([\d]*\/?)$",  # race ID
            re.IGNORECASE,
        )

        if not pattern.match(url):
            raise ValueError(f"invalid {url=}")
