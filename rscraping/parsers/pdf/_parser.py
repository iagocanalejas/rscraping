import logging
from typing import Protocol

from fitz import Page

from rscraping.data.models import Datasource, Lineup

logger = logging.getLogger(__name__)


class PdfParser(Protocol):
    DATASOURCE: Datasource

    def parse_lineup(self, page: Page) -> Lineup:
        ...
