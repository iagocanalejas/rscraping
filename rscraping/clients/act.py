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
    _html_parser: ACTHtmlParser
    _pdf_parser: ACTPdfParser

    DATASOURCE = Datasource.ACT
    MALE_START = 2003
    FEMALE_START = 2009

    def __init__(self, **_) -> None:
        super().__init__()
        self._html_parser = ACTHtmlParser()
        self._pdf_parser = ACTPdfParser()

    @override
    @staticmethod
    def get_race_details_url(race_id: str, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/ver.php?r={race_id}"

    @override
    @staticmethod
    def get_races_url(year: int, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/index.php?t={year}"

    @override
    @staticmethod
    def get_lineup_url(race_id: str, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/tripulacionespdf.php?r={race_id}"

    @override
    def get_lineup_by_race_id(self, race_id: str, is_female: bool, **_) -> Generator[Lineup, Any, Any]:
        url = self.get_lineup_url(race_id, is_female)
        raw_pdf = requests.get(url=url, headers=HTTP_HEADERS()).content

        with fitz.open("pdf", raw_pdf) as pdf:
            for page_num in range(pdf.page_count):
                lineup = self._pdf_parser.parse_lineup(page=pdf[page_num])
                if lineup:
                    yield lineup

    @override
    def get_race_ids_by_rower(self, **_):
        raise NotImplementedError
