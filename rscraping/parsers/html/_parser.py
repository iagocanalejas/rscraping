from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any

from parsel import Selector

from rscraping.data.models import Datasource, Lineup, Race, RaceName


class HtmlParser(ABC):
    DATASOURCE: Datasource

    @abstractmethod
    def parse_race(self, selector: Selector, **kwargs) -> Race | None:
        raise NotImplementedError

    @abstractmethod
    def parse_race_ids(self, selector: Selector, **kwargs) -> Generator[str, Any, Any]:
        raise NotImplementedError

    @abstractmethod
    def parse_race_names(self, selector: Selector, **kwargs) -> Generator[RaceName, Any, Any]:
        raise NotImplementedError

    @abstractmethod
    def parse_lineup(self, selector: Selector, **kwargs) -> Lineup:
        raise NotImplementedError
