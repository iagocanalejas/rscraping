from collections.abc import Generator
from datetime import datetime
from typing import Any, Protocol

from parsel.selector import Selector

from rscraping.data.models import Datasource, Race, RaceName


class HtmlParser(Protocol):
    DATASOURCE: Datasource

    def parse_race(self, selector: Selector, **kwargs) -> Race | None:
        """
        Parse the given Selector to retrieve the race object.

        Args:
            selector (Selector): The Selector to parse.
            **kwargs: Additional keyword arguments.

        Returns: Race | None: The race object or None.
        """
        ...

    def parse_race_ids(self, selector: Selector, **kwargs) -> Generator[str, Any, Any]:
        """
        Parse the given Selector to retrieve the IDs of the races.

        Args:
            selector (Selector): The Selector to parse.
            **kwargs: Additional keyword arguments.

        Yields: str: The IDs of the races.
        """
        ...

    def parse_race_ids_by_days(self, selector: Selector, days: list[datetime], **kwargs) -> Generator[str, Any, Any]:
        """
        Parse the given Selector to retrieve the IDs of the races that took place on the given days.

        Args:
            selector (Selector): The Selector to parse.
            days (list[datetime]): The days to filter
            **kwargs: Additional keyword arguments.

        Yields: str: The IDs of the races.
        """
        ...

    def parse_race_names(self, selector: Selector, **kwargs) -> Generator[RaceName, Any, Any]:
        """
        Parse the given Selector to retrieve the names of the races.

        Args:
            selector (Selector): The Selector to parse.
            **kwargs: Additional keyword arguments.

        Yields: RaceName: The names of the races.
        """
        ...
