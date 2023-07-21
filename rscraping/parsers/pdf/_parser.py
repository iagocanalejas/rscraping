import logging

from abc import ABC, abstractmethod
from pypdf import PageObject
from rscraping.data.models import Datasource, Lineup

logger = logging.getLogger(__name__)


class PdfParser(ABC):
    DATASOURCE: Datasource

    @abstractmethod
    def parse_lineup(self, page: PageObject) -> Lineup:
        raise NotImplementedError
