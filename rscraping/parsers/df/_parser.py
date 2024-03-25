from abc import ABC
from collections.abc import Generator
from typing import Any, override

from pandas import DataFrame

from rscraping.data.models import Datasource, Race

from ._protocol import DataFrameParserProtocol


class DataFrameParser(DataFrameParserProtocol, ABC):
    DATASOURCE: Datasource
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        source = kwargs.pop("source")
        super().__init_subclass__(**kwargs)
        cls._registry[source] = cls

    def __new__(cls, source: str, **_) -> "DataFrameParser":  # pragma: no cover
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)

        return final_obj

    @override
    def parse_races(self, data: DataFrame, **kwargs) -> Generator[Race, Any, Any]:
        raise NotImplementedError
