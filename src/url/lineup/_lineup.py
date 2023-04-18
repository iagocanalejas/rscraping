from abc import ABC, abstractmethod

from src.utils.models import LineUpItem


class LineupUrlParser(ABC):
    _registry = {}

    DATASOURCE: str

    def __init_subclass__(cls, **kwargs):
        source = kwargs.pop('source', None)
        super().__init_subclass__(**kwargs)
        if source:
            cls._registry[source] = cls

    def __new__(cls, source: str, **kwargs) -> 'LineupUrlParser':  # pragma: no cover
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)

        return final_obj

    @abstractmethod
    def parse_page(self, url: str) -> LineUpItem:
        raise NotImplementedError
