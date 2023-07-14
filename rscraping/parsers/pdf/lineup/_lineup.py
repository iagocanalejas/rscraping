import logging

from abc import ABC, abstractmethod
from pypdf import PageObject
from data.models import Datasource, Lineup

logger = logging.getLogger(__name__)


class LineupPdfParser(ABC):
    _registry = {}

    DATASOURCE: Datasource

    def __init_subclass__(cls, **kwargs):
        source = kwargs.pop("source", None)
        super().__init_subclass__(**kwargs)
        if source:
            cls._registry[source] = cls

    def __new__(cls, source: Datasource, **kwargs) -> "LineupPdfParser":  # pyright: ignore
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)

        return final_obj

    @abstractmethod
    def parse_page(self, page: PageObject) -> Lineup:
        raise NotImplementedError
