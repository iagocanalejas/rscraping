import os
from collections.abc import Generator
from typing import Any

from simplemma.simplemma import text_lemmatizer

from pyutils.strings import normalize_synonyms, remove_conjunctions, remove_symbols, unaccent
from rscraping.clients import Client
from rscraping.data.constants import SYNONYMS
from rscraping.data.models import Datasource, Race
from rscraping.ocr import ImageProcessor
from rscraping.parsers.df import DataFrameParser


def find_race(
    race_id: str,
    datasource: Datasource,
    is_female: bool,
    category: str | None = None,
    table: int | None = None,
) -> Race | None:
    """
    Find a race based on the provided parameters.

    Parameters:
    - race_id (str): The ID of the race to find.
    - datasource (Datasource): The data source to use for retrieving race information.
    - is_female (bool): Whether the race is for females (True) or not (False).
    - category (Optional[str]): The category of the race (optional).
    - table (Optional[int]): The day of the race (optional).

    Returns:
    - Optional[Race]: The found Race object if the race is found, otherwise None.
    """

    client = Client(source=datasource, is_female=is_female, category=category)
    return client.get_race_by_id(race_id, table=table)


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

    return parser.parse_races(
        data=df,
        file_name=os.path.splitext(os.path.basename(path))[0],
        header=header_data,
    )


def lemmatize(phrase: str, lang: str = "es") -> list[str]:
    """
    Lemmatize a phrase using the simplemma library. The phrase is preprocessed before lemmatization.
    Synonyms are normalized, conjunctions are removed, symbols are removed, and accents are removed.

    Parameters:
    - phrase (str): The phrase to lemmatize.
    - lang (str): The language of the phrase (default: "es").

    Returns: list[str]: A list of lemmatized words from the phrase.
    """
    phrase = normalize_synonyms(phrase, SYNONYMS)
    phrase = unaccent(remove_symbols(remove_conjunctions(phrase)))
    return list(set(text_lemmatizer(phrase, lang=lang)))
