from datetime import date
import logging
import requests

from ._client import Client
from io import BytesIO
from pypdf import PdfReader
from typing import List, Optional
from parsel import Selector
from data.constants import HTTP_HEADERS
from data.models import Datasource, Lineup, Race
from parsers.pdf import ACTPdfParser
from parsers.html import ACTHtmlParser


logger = logging.getLogger(__name__)


class ACTClient(Client, source=Datasource.ACT):
    DATASOURCE = Datasource.ACT

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

    def get_race_by_id(self, race_id: str, **_) -> Optional[Race]:
        url = self.get_race_details_url(race_id, self._is_female)
        race = ACTHtmlParser().parse_race(
            selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).text),
            race_id=race_id,
            is_female=self._is_female,
        )
        if race:
            race.url = url
        return race

    def get_race_ids_by_year(self, year: int, **_) -> List[str]:
        since = 2009 if self._is_female else 2003
        today = date.today().year
        if year < since or year > today:
            raise ValueError(f"invalid 'year', available values are [{since}, {today}]")

        url = self.get_races_url(year, self._is_female)
        return ACTHtmlParser().parse_race_ids(selector=Selector(requests.get(url=url, headers=HTTP_HEADERS).text))

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
