from abc import ABC

from rscraping.data.models import Datasource

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
