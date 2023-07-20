import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Type

from data.models import Datasource, Lineup, Race


logger = logging.getLogger(__name__)


class Client(ABC):
    _registry = {}

    DATASOURCE: Datasource

    def __init_subclass__(cls, **kwargs):
        source = kwargs.pop("source", None)
        super().__init_subclass__(**kwargs)
        if source:
            cls._registry[source] = cls

    def __new__(cls, source: Datasource, **kwargs) -> Type["Client"]:  # pyright: ignore
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)

        return final_obj

    ####################################################
    #                     ABSTRACT                     #
    ####################################################

    @staticmethod
    @abstractmethod
    def get_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_lineup_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_race_by_id(self, race_id: str, **kwargs) -> Optional[Race]:
        raise NotImplementedError

    @abstractmethod
    def get_lineup_by_race_id(self, race_id: str, **kwargs) -> List[Lineup]:
        raise NotImplementedError
