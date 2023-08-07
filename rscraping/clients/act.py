from io import BytesIO
from typing import List

import requests
from pypdf import PdfReader

from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup
from rscraping.parsers.html import ACTHtmlParser
from rscraping.parsers.pdf import ACTPdfParser

from ._client import Client


class ACTClient(Client, source=Datasource.ACT):
    _html_parser: ACTHtmlParser

    DATASOURCE = Datasource.ACT
    MALE_START = 2003
    FEMALE_START = 2009

    def __init__(self, **_) -> None:
        super().__init__()
        self._html_parser = ACTHtmlParser()

    @staticmethod
    def get_race_details_url(race_id: str, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/ver.php?r={race_id}"

    @staticmethod
    def get_races_url(year: int, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/index.php?t={year}"

    @staticmethod
    def get_lineup_url(race_id: str, is_female: bool, **_) -> str:
        female = "/femenina" if is_female else ""
        return f"https://www.euskolabelliga.com{female}/resultados/tripulacionespdf.php?r={race_id}"

    def get_lineup_by_race_id(self, race_id: str, **_) -> List[Lineup]:
        url = self.get_lineup_url(race_id, self._is_female)
        raw_pdf = requests.get(url=url, headers=HTTP_HEADERS).content

        parsed_items: List[Lineup] = []
        parser = ACTPdfParser()

        with BytesIO(raw_pdf) as pdf:
            for page in PdfReader(pdf).pages:
                items = parser.parse_lineup(page=page)
                if items:
                    parsed_items.append(items)

        return parsed_items
