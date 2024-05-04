from simplemma.simplemma import text_lemmatizer

from pyutils.strings import normalize_synonyms, remove_conjunctions, remove_symbols, unaccent
from rscraping.clients import Client
from rscraping.data.constants import SYNONYMS
from rscraping.data.models import Datasource, Race


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
