from abc import ABC, abstractmethod
from typing import Any, Generator, Optional

from parsel import Selector

from rscraping.data.models import Datasource, Lineup, Race, RaceName


class HtmlParser(ABC):
    DATASOURCE: Datasource

    @abstractmethod
    def parse_race(self, selector: Selector, **kwargs) -> Optional[Race]:
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
