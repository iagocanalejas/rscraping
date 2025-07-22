import re
from typing import override

from rscraping.data.constants import GENDER_FEMALE
from rscraping.data.models import Datasource
from rscraping.parsers.html.ete import ETEHtmlParser

from ._client import Client


class ETEClient(Client, source=Datasource.ETE):
    _gender = GENDER_FEMALE

    DATASOURCE = Datasource.ETE
    FEMALE_START = 2018

    @property
    def _html_parser(self) -> ETEHtmlParser:
        return ETEHtmlParser()

    @override
    def _is_valid_gender(self, gender: str) -> bool:
        return gender in [GENDER_FEMALE]

    @property
    def is_female(self) -> bool:
        return True

    @override
    def get_race_details_url(self, race_id: str, **_) -> str:
        return f"https://www.ligaete.com/es/regata/{race_id}/unknown"

    @override
    def get_races_url(self, year: int, **_) -> str:
        return f"https://www.ligaete.com/es/calendario/{year}"

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
