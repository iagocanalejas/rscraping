import logging
from abc import ABC, abstractmethod

from fitz import Page

from rscraping.data.models import Datasource, Lineup

logger = logging.getLogger(__name__)


class PdfParser(ABC):
    DATASOURCE: Datasource

    @abstractmethod
    def parse_lineup(self, page: Page) -> Lineup:
        raise NotImplementedError
