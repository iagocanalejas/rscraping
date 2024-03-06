from collections.abc import Generator
from typing import Any, Protocol

from parsel.selector import Selector

from rscraping.data.models import Datasource, Lineup, Race, RaceName


class HtmlParser(Protocol):
    DATASOURCE: Datasource

    def parse_race(self, selector: Selector, **kwargs) -> Race | None: ...

    def parse_race_ids(self, selector: Selector, **kwargs) -> Generator[str, Any, Any]: ...

    def parse_race_names(self, selector: Selector, **kwargs) -> Generator[RaceName, Any, Any]: ...

    def parse_lineup(self, selector: Selector, **kwargs) -> Lineup: ...
