from collections.abc import Generator
from typing import Any, Protocol

from pandas import DataFrame

from rscraping.data.models import Race


class DataFrameParserProtocol(Protocol):
    def parse_races_from(self, data: DataFrame, *_, **kwargs) -> Generator[Race, Any, Any]: ...
