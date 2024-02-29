import os
from typing import Any
from collections.abc import Generator

from pyutils.strings import normalize_synonyms, remove_conjunctions, remove_symbols
from pyutils.shortcuts import only_one_not_none
from rscraping.clients import Client
from rscraping.clients.gdrive import GoogleDriveClient
from rscraping.data.constants import SYNONYMS
from rscraping.data.models import Datasource, Lineup, Race
from simplemma.simplemma import text_lemmatizer

from rscraping.ocr import ImageProcessor
from rscraping.parsers.df import DataFrameParser


def find_race(
    race_id: str,
    datasource: Datasource,
    is_female: bool,
    day: int | None = None,
    with_lineup: bool = False,
) -> Race | None:
    """
    Find a race based on the provided parameters.

    Parameters:
    - race_id (str): The ID of the race to find.
    - datasource (Datasource): The data source to use for retrieving race information.
    - is_female (bool): Whether the race is for females (True) or not (False).
    - day (Optional[int]): The day of the race (optional).
    - with_lineup (bool): Whether to include lineup information for participants (default: False).

    Returns:
    - Optional[Race]: The found Race object if the race is found, otherwise None.

    This function retrieves race information using the provided datasource and parameters.
    If with_lineup is True, it attempts to find lineup information for each participant in the race and attaches it to
    the participant object.

    Note that lineup retrieval may raise NotImplementedError, in which case it will be caught and
    the function will proceed without adding lineup information.
    """

    client = Client(source=datasource)  # type: ignore
    race = client.get_race_by_id(race_id, day=day, is_female=is_female)

    if race is not None and with_lineup:
        try:
            lineups = client.get_lineup_by_race_id(race_id, is_female=is_female)
            for participant in race.participants:
                lineup = [lin for lin in lineups if lin.club == participant.participant]
                participant.lineup = lineup[0] if len(lineup) == 1 else None
        except NotImplementedError:
            pass

    return race


def find_csv_race(
    race_id: str, sheet_id: str | None, file_path: str | None, is_female: bool, sheet_name: str | None = None
) -> Race | None:
    """
    Find a race inside a Google Sheet by its ID or in a file.

    Parameters:
    - race_id (str): The ID of the race to find.
    - sheet_id (Optional[str]): The ID of the Google Sheet to search in.
    - file_path (Optional[str]): The path to the local file to search in.
    - is_female (bool): Whether the race is for females (True) or not (False).
    - sheet_name (Optional[str]): The name of the sheet to search in (optional).

    Returns:
    - Optional[Race]: The found Race object if the race is found, otherwise None.

    This function retrieves the race information using a Google Drive sheet.
    """
    client = GoogleDriveClient()
    return client.get_race_by_id(
        race_id, sheet_id=sheet_id, file_path=file_path, sheet_name=sheet_name, is_female=is_female
    )


def parse_race_csv(
    *_, sheet_id: str | None, file_path: str | None, is_female: bool, sheet_name: str | None
) -> Generator[Race, Any, Any]:
    """
    Parse race information from a Google Sheet or file using provided parameters.

    Parameters:
    - sheet_id (Optional[str]): The ID of the Google Sheet to parse.
    - file_path (Optional[str]): The path to the local file to search in.
    - is_female (bool): Whether the race is for females (True) or not (False).
    - sheet_name (Optional[str]): The name of the sheet to parse (optional).

    Returns:
    - Generator[Race, Any, Any]: A generator that yields Race objects as they are parsed.
    """

    client = GoogleDriveClient()
    return client.get_races(sheet_id=sheet_id, file_path=file_path, sheet_name=sheet_name, is_female=is_female)


def parse_race_image(
    path: str,
    datasource: Datasource,
    header_size: int = 3,
    allow_plot: bool = False,
) -> Generator[Race, Any, Any]:
    """
    Parse race information from an image file using provided data source and parameters.

    Parameters:
    - path (str): The path to the image file to be processed.
    - datasource (Datasource): The data source to use for retrieving additional data.
    - header_size (int): The ammount of the image that represents the header (default: 3) -> 1/3.
    - allow_plot (bool): Whether to allow plotting for debugging during processing (default: False).

    Yields:
    - Generator[Race, Any, Any]: A generator that yields Race objects as they are parsed.

    This function processes race information from an image file. It uses an ImageProcessor and a
    DataFrameParser for retrieving header data and tabular data from the image, respectively.
    The header data is retrieved based on the specified header size, and the tabular data is
    extracted using the DataFrameParser.

    The function yields Race objects as they are parsed from the data. The file name, header data,
    and tabular data are used as input for the parsing process.
    """

    processor = ImageProcessor(source=datasource, allow_plot=allow_plot)  # pyright: ignore
    parser = DataFrameParser(source=datasource, allow_plot=allow_plot)  # pyright: ignore

    header_data = processor.retrieve_header_data(path=path, header_size=header_size)
    df = processor.retrieve_tabular_dataframe(path=path, header_size=header_size)

    return parser.parse_races_from(
        data=df,
        file_name=os.path.splitext(os.path.basename(path))[0],
        header=header_data,
    )


def find_lineup(race_id: str, datasource: Datasource, is_female: bool) -> Generator[Lineup, Any, Any]:
    client = Client(source=datasource)  # type: ignore
    return client.get_lineup_by_race_id(race_id, is_female=is_female)


def lemmatize(phrase: str, lang: str = "es") -> list[str]:
    phrase = normalize_synonyms(phrase, SYNONYMS)
    phrase = remove_symbols(remove_conjunctions(phrase))
    return list(set(text_lemmatizer(phrase, lang=lang)))
