from collections.abc import Generator
from typing import Protocol

from pandas import DataFrame

from rscraping.data.models import Race


class DataFrameParserProtocol(Protocol):
    def parse_races(self, data: DataFrame, **kwargs) -> Generator[Race]:
        """
        Parse the given DataFrame to retrieve the Race objects.

        Args:
            data (DataFrame): The DataFrame to parse.
            **kwargs: Additional keyword arguments.

        Yields: Race: The parsed races.
        """
        ...
