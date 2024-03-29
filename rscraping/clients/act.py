import re
from collections.abc import Generator
from typing import Any, override

import fitz
import requests

from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup
from rscraping.parsers.html import ACTHtmlParser
from rscraping.parsers.pdf import ACTPdfParser

from ._client import Client


class ACTClient(Client, source=Datasource.ACT):
    DATASOURCE = Datasource.ACT
    MALE_START = 2003
    FEMALE_START = 2009

    @property
    def _html_parser(self) -> ACTHtmlParser:
        return ACTHtmlParser()

    @property
    def _pdf_parser(self) -> ACTPdfParser:
        return ACTPdfParser()

    @override
    @staticmethod
    def get_race_details_url(race_id: str, *, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/ver.php?r={race_id}"

    @override
    @staticmethod
    def get_races_url(year: int, *, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/index.php?t={year}"

    @override
    @staticmethod
    def get_lineup_url(race_id: str, *, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/tripulacionespdf.php?r={race_id}"

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

    @override
    def get_lineup_by_race_id(self, race_id: str, **__) -> Generator[Lineup, Any, Any]:
        url = self.get_lineup_url(race_id, is_female=self._is_female)
        raw_pdf = requests.get(url=url, headers=HTTP_HEADERS()).content

        with fitz.open("pdf", raw_pdf) as pdf:
            for page_num in range(pdf.page_count):
                lineup = self._pdf_parser.parse_lineup(page=pdf[page_num])
                if lineup:
                    yield lineup
