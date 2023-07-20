import logging

from abc import ABC, abstractmethod
import re
from typing import Optional
from parsel import Selector
from pyutils.strings import find_roman, roman_to_int
from data.models import Datasource, Lineup, Race

logger = logging.getLogger(__name__)


class HtmlParser(ABC):
    DATASOURCE: Datasource

    @staticmethod
    def get_edition(name: str) -> int:
        name = re.sub(r"[\'\".:]", " ", name)

        roman_options = list(filter(None, [find_roman(w) for w in name.split()]))
        return roman_to_int(roman_options[0]) if roman_options else 1

    @abstractmethod
    def parse_race(self, selector: Selector, **kwargs) -> Optional[Race]:
        raise NotImplementedError

    @abstractmethod
    def parse_lineup(self, selector: Selector, **kwargs) -> Lineup:
        raise NotImplementedError
