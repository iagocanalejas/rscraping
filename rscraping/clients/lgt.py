import re
from collections.abc import Generator
from datetime import date
from typing import Any, override

import requests
from fitz import fitz
from parsel.selector import Selector

from pyutils.strings import whitespaces_clean
from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource, Lineup, Race, RaceName
from rscraping.parsers.html import LGTHtmlParser
from rscraping.parsers.pdf import LGTPdfParser

from ._client import Client


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

    DATASOURCE = Datasource.LGT
    MALE_START = FEMALE_START = 2020

    @property
    def _html_parser(self) -> LGTHtmlParser:
        return LGTHtmlParser()

    @property
    def _pdf_parser(self) -> LGTPdfParser:
        return LGTPdfParser()

    @override
    @staticmethod
    def get_race_details_url(race_id: str, **_) -> str:
        return f"https://www.ligalgt.com/principal/regata/{race_id}"

    @override
    @staticmethod
    def get_lineup_url(race_id: str, **_) -> str:
        return f"https://www.ligalgt.com/pdf/alinacion.php?regata_id={race_id}"

    @staticmethod
    def get_results_selector(race_id: str) -> Selector:
        url = "https://www.ligalgt.com/ajax/principal/ver_resultados.php"
        data = {"liga_id": 1, "regata_id": race_id}
        return Selector(requests.post(url=url, headers=HTTP_HEADERS(), data=data).content.decode("utf-8"))

    @staticmethod
    def get_calendar_selector() -> Selector:
        url = "https://www.ligalgt.com/ajax/principal/regatas.php"
        data = {"lng": "es"}
        return Selector(requests.post(url=url, headers=HTTP_HEADERS(), data=data).content.decode("utf-8"))

    @override
    def validate_url(self, url: str):
        pattern = re.compile(
            r"^(https?:\/\/)?"  # Scheme (http, https, or empty)
            r"(www\.ligalgt\.com\/principal\/regata\/)"  # Domain name
            r"([\d]*\/?)$",  # race ID
            re.IGNORECASE,
        )

        if not pattern.match(url):
            raise ValueError(f"invalid {url=}")

    @override
    def get_race_by_id(self, race_id: str, *_, **kwargs) -> Race | None:
        if race_id in self._excluded_ids:
            return None

        kwargs["results_selector"] = self.get_results_selector(race_id)
        return super().get_race_by_id(race_id, **kwargs)

    @override
    def get_race_by_url(self, url: str, race_id: str, **kwargs):
        if race_id in self._excluded_ids:
            return None

        kwargs["results_selector"] = self.get_results_selector(race_id)
        return super().get_race_by_url(url, race_id, **kwargs)

    @override
    def get_race_names_by_year(self, year: int, **_) -> Generator[RaceName, Any, Any]:
        today = date.today().year
        if today == year:
            race_names = self._html_parser.parse_race_names(selector=self.get_calendar_selector())
            if race_names:
                yield from race_names
                return

        for id in self.get_race_ids_by_year(year, is_female=self._is_female):
            if id in self._excluded_ids:
                pass

            url = self.get_race_details_url(id)
            selector = Selector(requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8"))
            if self._html_parser.is_valid_race(selector):
                name = self._html_parser.get_name(selector)
                yield RaceName(race_id=id, name=whitespaces_clean(name).upper())

    @override
    def get_race_ids_by_year(self, year: int, **_) -> Generator[str, Any, Any]:
        """
        Find the IDs of the races that took place in a given year.

        As the LGT datasource doesn't give us an easy way of retrieving the races for a given year we need to bruteforce
        it, this method will do a binary search for the 'upper' and 'lower' bounds of a season.

        We also need to ignore a hole ton of useless IDs (_excluded_ids) that are not used or have invalid information.

        NOTE: For the current year it first tryies to find the IDs in the calendar page.

        Args:
            year (int): The year for which to find the IDs.
            **kwargs: Additional keyword arguments.

        Yields: str: Unchecked race IDs, note that *this list can contain invalid IDs* as this method does not check
        each one of them.
        """
        today = date.today().year
        if today == year:
            race_ids = self._html_parser.parse_race_ids(selector=self.get_calendar_selector())
            if race_ids:
                yield from race_ids
                return

        self.validate_year(year)
        since = self.MALE_START

        # asume 30 races per year for lower bound and 50 for the upper bound
        left, right = (year - since) * 20, (today - since + 1) * 50
        while left <= right:
            mid = left + (right - left) // 2
            while mid in self._excluded_ids and mid > (left + 1):
                mid -= 1

            race_year = self._get_race_year(str(mid))
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

            race_year = self._get_race_year(str(mid))
            if not race_year or race_year > year:
                right = mid - 1
            else:
                left = mid + 1
        upper_race_id = right

        return (str(r) for r in range(lower_race_id, (upper_race_id + 1)) if r not in self._excluded_ids)

    @override
    def get_lineup_by_race_id(self, race_id: str, **_) -> Generator[Lineup, Any, Any]:
        if race_id in self._excluded_ids:
            return

        url = self.get_lineup_url(race_id)
        raw_pdf = requests.get(url=url, headers=HTTP_HEADERS()).content

        with fitz.open("pdf", raw_pdf) as pdf:
            for page_num in range(pdf.page_count):
                lineup = self._pdf_parser.parse_lineup(page=pdf[page_num])
                if lineup:
                    yield lineup

    ####################################################
    #                      UTILS                       #
    ####################################################

    _RACE_YEARS: dict[str, int | None] = {}

    def _get_race_year(self, race_id: str) -> int | None:
        if race_id in self._RACE_YEARS:
            return self._RACE_YEARS[race_id]

        url = self.get_race_details_url(race_id)

        selector = Selector(requests.get(url=url, headers=HTTP_HEADERS()).text)
        if not self._html_parser.is_valid_race(selector):
            self._RACE_YEARS[race_id] = None
            return None
        race_year = self._html_parser.get_date(selector).year

        self._RACE_YEARS[race_id] = race_year
        return race_year
