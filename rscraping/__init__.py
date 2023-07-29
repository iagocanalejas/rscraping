from typing import List, Optional

from pyutils.strings import normalize_synonyms, remove_conjunctions, remove_symbols
from rscraping.clients import Client
from rscraping.data.constants import SYNONYMS
from rscraping.data.models import Datasource, Lineup, Race
from simplemma import text_lemmatizer


def find_lineup(race_id: str, datasource: Datasource, is_female: bool) -> List[Lineup]:
    client = Client(source=datasource, is_female=is_female)  # type: ignore
    return client.get_lineup_by_race_id(race_id)


def find_race(race_id: str, datasource: Datasource, is_female: bool, day: Optional[int] = None) -> Optional[Race]:
    client = Client(source=datasource, is_female=is_female)  # type: ignore
    return client.get_race_by_id(race_id, is_female=is_female, day=day)


def lemmatize(phrase: str, lang: str = "es") -> List[str]:
    phrase = normalize_synonyms(phrase, SYNONYMS)
    phrase = remove_symbols(remove_conjunctions(phrase))
    return list(set(text_lemmatizer(phrase, lang=lang)))
