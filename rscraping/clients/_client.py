import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from rscraping.data.models import Datasource, Lineup, Race


logger = logging.getLogger(__name__)


class Client(ABC):
    _registry = {}
    _is_female = False

    DATASOURCE: Datasource

    def __init_subclass__(cls, **kwargs):
        source = kwargs.pop("source", None)
        super().__init_subclass__(**kwargs)
        if source:
            cls._registry[source] = cls

    def __new__(cls, source: Datasource, is_female: bool = False, **kwargs) -> "Client":  # pyright: ignore
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)
        final_obj._is_female = is_female

        return final_obj

    ####################################################
    #                     ABSTRACT                     #
    ####################################################

    @staticmethod
    @abstractmethod
    def get_race_details_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_races_url(year: int, **kwargs) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_lineup_url(race_id: str, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_race_by_id(self, race_id: str, **kwargs) -> Optional[Race]:
        raise NotImplementedError

    @abstractmethod
    def get_race_ids_by_year(self, year: int, **kwargs) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def get_lineup_by_race_id(self, race_id: str, **kwargs) -> List[Lineup]:
        raise NotImplementedError
