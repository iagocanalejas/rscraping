import logging
import requests


from ._client import Client
from io import BytesIO
from pypdf import PdfReader
from typing import List, Optional
from parsel import Selector
from data.constants import HTTP_HEADERS
from data.models import Datasource, Lineup, Race
from parsers.html import LGTHtmlParser
from parsers.pdf import LGTPdfParser

logger = logging.getLogger(__name__)


class LGTClient(Client, source=Datasource.LGT):
    DATASOURCE = Datasource.LGT

    @staticmethod
    def get_url(race_id: str, **_) -> str:
        return f"https://www.ligalgt.com/principal/regata/{race_id}"

    @staticmethod
    def get_lineup_url(race_id: str, **_) -> str:
        return f"https://www.ligalgt.com/pdf/alinacion.php?regata_id={race_id}"

    @staticmethod
    def get_results_selector(race_id: str) -> Selector:
        url = "https://www.ligalgt.com/ajax/principal/ver_resultados.php"
        data = {"liga_id": 1, "regata_id": race_id}
        return Selector(requests.post(url=url, headers=HTTP_HEADERS, data=data).text)

    def get_race_by_id(self, race_id: str, **_) -> Optional[Race]:
        url = self.get_url(race_id)
        self._selector = Selector(requests.get(url=url, headers=HTTP_HEADERS).text)
        self._results_selector = self.get_results_selector(race_id)

        race = LGTHtmlParser().parse_race(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).text),
            results_selector=self.get_results_selector(race_id),
            race_id=race_id,
        )
        if race:
            race.url = url
        return race

    def get_lineup_by_race_id(self, race_id: str, **_) -> List[Lineup]:
        url = self.get_lineup_url(race_id)
        raw_pdf = requests.get(url=url, headers=HTTP_HEADERS).content

        parsed_items: List[Lineup] = []
        parser = LGTPdfParser()

        with BytesIO(raw_pdf) as pdf:
            for page in PdfReader(pdf).pages:
                items = parser.parse_lineup(page=page)
                if items:
                    parsed_items.append(items)

        return parsed_items
