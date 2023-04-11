import logging
from abc import ABC, abstractmethod

from pypdf import PageObject

from src.utils.models import LineUpItem

logger = logging.getLogger(__name__)


class LineUpParser(ABC):
    _registry = {}

    DATASOURCE: str

    def __init_subclass__(cls, **kwargs):
        source = kwargs.pop('source', None)
        super().__init_subclass__(**kwargs)
        if source:
            cls._registry[source] = cls

    def __new__(cls, source: str, **kwargs) -> 'LineUpParser':  # pragma: no cover
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)

        return final_obj

    @abstractmethod
    def parse_page(self, page: PageObject) -> LineUpItem:
        raise NotImplementedError
