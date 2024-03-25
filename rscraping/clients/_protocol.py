from collections.abc import Generator
from typing import Any, Protocol

from rscraping.data.models import Datasource, Lineup, Race, RaceName
from rscraping.parsers.html import HtmlParser
from rscraping.parsers.pdf import PdfParser


class ClientProtocol(Protocol):
    DATASOURCE: Datasource
    FEMALE_START: int
    MALE_START: int

    _is_female: bool = False

    @property
    def _html_parser(self) -> HtmlParser: ...

    @property
    def _pdf_parser(self) -> PdfParser: ...

    def validate_year(self, year: int):
        """
        Checks the given year for the current datasource raising a ValueError if it's outside the range.

        Args:
            year (int): The year to validate.

        Raises: ValueError: If the year is outside the valid range.
        """
        ...

    def validate_url(self, url: str):
        """
        Checks the given url for the current datasource, raising a ValueError if it's invalid.

        Args:
            url (str): The URL to validate.

        Raises: ValueError: If the url is invalid.
        """
        ...

    def get_race_by_id(self, race_id: str, **kwargs) -> Race | None:
        """
        Retrieve race details by ID parsing data from the corresponding datasource.

        Args:
            race_id (str): The ID of the race.
            **kwargs: Additional keyword arguments.

        Returns: Race | None: The parsed race details or None if the race is not found.
        """
        ...

    def get_race_by_url(self, url: str, race_id: str, **kwargs) -> Race | None:
        """
        Retrieve race details by parsing data from the corresponding datasource.

        Args:
            url (str): The URL of the race.
            race_id (str): The ID of the race.
            **kwargs: Additional keyword arguments.

        Returns: Race | None: The parsed race details or None if the race is not found.
        """
        ...

    def get_race_names_by_year(self, year: int, **kwargs) -> Generator[RaceName, Any, Any]:
        """
        Find the names of the races that took place in a given year.

        Args:
            year (int): The year for which find the names.
            **kwargs: Additional keyword arguments.

        Yields: RaceName: Race names.
        """
        ...

    def get_race_ids_by_year(self, year: int, **kwargs) -> Generator[str, Any, Any]:
        """
        Find the IDs of the races that took place in a given year.

        Args:
            year (int): The year for which to find the IDs.
            **kwargs: Additional keyword arguments.

        Yields: str: Race IDs.
        """
        ...

    def get_race_ids_by_club(self, club_id: str, year: int, **kwargs) -> Generator[str, Any, Any]:
        """
        Find the IDs for the races in witch a given club participated in a given year.

        Args:
            club_id (str): The ID of the club.
            year (int): The year for which to find race IDs.
            **kwargs: Additional keyword arguments.

        Yields: str: Race IDs.
        """
        ...

    def get_lineup_by_race_id(self, race_id: str, **kwargs) -> Generator[Lineup, Any, Any]:
        """
        Get the lineups for a specific race.

        Args:
            race_id (str): The ID of the race.
            **kwargs: Additional keyword arguments.

        Yields: Lineup: Lineups for the race.
        """
        ...

    @staticmethod
    def get_race_details_url(race_id: str, **kwargs) -> str:
        """
        Return the URL for retrieving details of a specific race.
        """
        ...

    @staticmethod
    def get_races_url(year: int, **kwargs) -> str:
        """
        Return the URL for retrieving races in a specific year.
        """
        ...

    @staticmethod
    def get_lineup_url(race_id: str, **kwargs) -> str:
        """
        Return the URL for retrieving the lineup of a specific race.
        """
        ...
