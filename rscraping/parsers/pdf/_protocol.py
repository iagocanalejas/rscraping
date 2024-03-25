from typing import Protocol

from fitz import Page

from rscraping.data.models import Datasource, Lineup


class PdfParser(Protocol):
    DATASOURCE: Datasource

    def parse_lineup(self, page: Page) -> Lineup | None:
        """
        Parse the given PDF page to retrieve the Lineup object.

        Args:
            page (Page): The PDF page to parse.

        Returns: Lineup | None: The parsed lineup or None if the lineup is not found.
        """
        ...
