import logging
from abc import ABC, abstractmethod
from typing import Any, Generator

from pandas import DataFrame

from rscraping.data.models import Datasource, Race

logger = logging.getLogger(__name__)


class DataFrameParser(ABC):
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

    ####################################################
    #                 ABSTRACT METHODS                 #
    ####################################################

    @abstractmethod
    def parse_races_from(self, file_name: str, header: str, tabular: DataFrame, **kwargs) -> Generator[Race, Any, Any]:
        raise NotImplementedError
