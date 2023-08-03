import requests
from datetime import date
from pyutils.strings import remove_parenthesis, remove_roman, whitespaces_clean
from ._client import Client
from io import BytesIO
from pypdf import PdfReader
from typing import Dict, List, Optional
from parsel import Selector
from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup, Race, RaceName
from rscraping.parsers.html import LGTHtmlParser
from rscraping.parsers.pdf import LGTPdfParser
from rscraping.data.normalization.races import normalize_race_name


class LGTClient(Client, source=Datasource.LGT):
    _excluded_ids = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        13,
        14,
        15,
        23,
        25,
        26,
        27,
        28,
        31,
        32,
        33,
        34,
        36,
        37,
        40,
        41,
        44,
        50,
        51,
        54,
        55,
        56,
        57,
        58,
        59,
        75,
        88,
        94,
        95,
        96,
        97,
        98,
        99,
        103,
        104,
        105,
        106,
        108,
        125,
        131,
        137,
        138,
        146,
        147,
        151,
    ]  # weird races
    _html_parser: LGTHtmlParser

    DATASOURCE = Datasource.LGT
    MALE_START = FEMALE_START = 2020

    def __init__(self, **_) -> None:
        super().__init__()
        self._html_parser = LGTHtmlParser()

    @staticmethod
    def get_race_details_url(race_id: str, **_) -> str:
        return f"https://www.ligalgt.com/principal/regata/{race_id}"

    @staticmethod
    def get_races_url(**_) -> str:
        raise NotImplementedError

    @staticmethod
    def get_lineup_url(race_id: str, **_) -> str:
        return f"https://www.ligalgt.com/pdf/alinacion.php?regata_id={race_id}"

    @staticmethod
    def get_results_selector(race_id: str) -> Selector:
        url = "https://www.ligalgt.com/ajax/principal/ver_resultados.php"
        data = {"liga_id": 1, "regata_id": race_id}
        return Selector(requests.post(url=url, headers=HTTP_HEADERS, data=data).text)

    def get_race_by_id(self, race_id: str, **kwargs) -> Optional[Race]:
        if race_id in self._excluded_ids:
            return None

        kwargs["results_selector"] = self.get_results_selector(race_id)
        return super().get_race_by_id(race_id, **kwargs)

    def get_race_ids_by_year(self, year: int, **_) -> List[str]:
        """
        As this datasource doesn't give us an easy way of retrieving the races for a given year we need to bruteforce
        it, this method will do a binary search for the 'upper' and 'lower' bounds of a season.

        We also need to ignore a hole ton of useless IDs (_excluded_ids) that are not used or have invalid information.

        Returns a list of unchecked IDs, note that this list can contain invalid values as this method does not check
        each one of them.
        """
        self.validate_year_or_raise_exception(year)

        since = self.MALE_START
        today = date.today().year
        parser = LGTHtmlParser()

        # asume 30 races per year for lower bound and 50 for the upper bound
        left, right = (year - since) * 20, (today - since + 1) * 50
        while left <= right:
            mid = left + (right - left) // 2
            while mid in self._excluded_ids and mid > (left + 1):
                mid -= 1

            race_year = self._get_race_year(parser, str(mid))
            if not race_year or race_year < year:
                left = mid + 1
            else:
                right = mid - 1
        lower_race_id = left

        # asume 30 races per year for lower bound and 50 for the upper bound
        left, right = (year - since) * 30, (today - since + 1) * 50
        while left <= right:
            mid = left + (right - left) // 2
            while mid in self._excluded_ids and mid < (right - 1):
                mid += 1

            race_year = self._get_race_year(parser, str(mid))
            if not race_year or race_year > year:
                right = mid - 1
            else:
                left = mid + 1
        upper_race_id = right

        return [str(r) for r in range(lower_race_id, (upper_race_id + 1)) if r not in self._excluded_ids]

    def get_race_names_by_year(self, year: int, **_) -> List[RaceName]:
        def normalize(parser: LGTHtmlParser, name: str, is_female: bool) -> str:
            name = normalize_race_name(name, is_female)
            name = remove_roman(remove_parenthesis(name))
            return parser._normalize_race_name(name)

        ids = self.get_race_ids_by_year(year)
        race_names: List[RaceName] = []
        parser = LGTHtmlParser()

        for id in ids:
            if id in self._excluded_ids:
                pass

            url = self.get_race_details_url(id)
            selector = Selector(requests.get(url=url, headers=HTTP_HEADERS).content.decode("utf-8"))
            if parser.is_valid_race(selector):
                name = parser.get_name(selector)
                is_female = any(e in name for e in ["FEMENINA", "FEMININA"])
                race_names.append(RaceName(id, whitespaces_clean(name).upper(), normalize(parser, name, is_female)))

        return race_names

    def get_lineup_by_race_id(self, race_id: str, **_) -> List[Lineup]:
        if race_id in self._excluded_ids:
            return []

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

    ####################################################
    #                      UTILS                       #
    ####################################################

    _RACE_YEARS: Dict[str, Optional[int]] = {}

    def _get_race_year(self, parser: LGTHtmlParser, race_id: str) -> Optional[int]:
        if race_id in self._RACE_YEARS:
            return self._RACE_YEARS[race_id]

        url = self.get_race_details_url(race_id)

        selector = Selector(requests.get(url=url, headers=HTTP_HEADERS).text)
        if not parser.is_valid_race(selector):
            self._RACE_YEARS[race_id] = None
            return None
        race_year = parser.get_date(selector).year

        self._RACE_YEARS[race_id] = race_year
        return race_year
