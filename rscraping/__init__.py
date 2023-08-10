import os
from typing import Any, Generator, List, Optional

from pyutils.strings import normalize_synonyms, remove_conjunctions, remove_symbols
from rscraping.clients import Client
from rscraping.data.constants import SYNONYMS
from rscraping.data.models import Datasource, Lineup, Race
from simplemma.simplemma import text_lemmatizer

from rscraping.ocr import ImageProcessor
from rscraping.parsers.ocr import OcrParser


def find_race(
    race_id: str,
    datasource: Datasource,
    is_female: bool,
    day: Optional[int] = None,
    with_lineup: bool = False,
) -> Optional[Race]:
    client = Client(source=datasource, is_female=is_female)  # type: ignore
    race = client.get_race_by_id(race_id, is_female=is_female, day=day)
    if race is not None and with_lineup:
        try:
            lineups = find_lineup(race_id, datasource, is_female=is_female)
            for participant in race.participants:
                lineup = [lin for lin in lineups if lin.club == participant.participant]
                participant.lineup = lineup[0] if len(lineup) == 1 else None
        except NotImplementedError:
            pass
    return race


def parse_race_image(
    path: str,
    datasource: Datasource,
    allow_plot: bool = False,
) -> Generator[Race, Any, Any]:
    processor = ImageProcessor(source=datasource, allow_plot=allow_plot)  # pyright: ignore
    parser = OcrParser(source=datasource, allow_plot=allow_plot)  # pyright: ignore

    header_data = processor.retrieve_header_data(path=path)
    df = processor.retrieve_tabular_dataframe(path=path)
    return parser.parse_races_from(
        file_name=os.path.splitext(os.path.basename(path))[0], header=header_data, tabular=df
    )


def find_lineup(race_id: str, datasource: Datasource, is_female: bool) -> List[Lineup]:
    client = Client(source=datasource, is_female=is_female)  # type: ignore
    return client.get_lineup_by_race_id(race_id)


def lemmatize(phrase: str, lang: str = "es") -> List[str]:
    phrase = normalize_synonyms(phrase, SYNONYMS)
    phrase = remove_symbols(remove_conjunctions(phrase))
    return list(set(text_lemmatizer(phrase, lang=lang)))
