import re

from pyutils.shortcuts import none
from pyutils.strings import (
    apply_replaces,
    find_roman,
    int_to_roman,
    match_normalization,
    remove_parenthesis,
    remove_roman,
    roman_to_int,
    whitespaces_clean,
)
from rscraping.data.checks import is_play_off
from rscraping.data.normalization.leagues import LEAGUE_KEYWORDS

_MISSPELLINGS = {
    "": ["RECICLAMOS LA LUZ", " AE ", "EXCMO", "ILTMO"],
    "IKURRIÑA": ["IKURIÑA", "IKURINA", "IÑURRIÑA"],
    "PIRATA.COM": ["PIRATA COM"],
    "PlAY OFF": ["PAY OFF"],
    "CASTILLA LA": ["CASTILLA - LA"],
    "AYUNTAMIENTO": ["AYTO"],
    "TRAIÑEIRAS": ["TRAIEIRAS"],
}

# tuples of sponsor name and if it should be replaced when found
_KNOWN_RACE_SPONSORS = [
    ("CEFYCAL", True),
    ("FANDICOSTA", False),
    ("ONURA HOMES", True),
    ("SALGADO CONGELADOS", False),
    ("WOFCO", True),
    ("YURRITA GROUP", True),
    ("YURRITA", True),
]

_KO_NAMES = {
    "ALGORTAKO": ["ALGORTA"],
    "AREATAKO": ["AREATA"],
    "BERMEOKO": ["BERMEO"],
    "ELANTXOBEKO": ["ELANTXOBE"],
    "ERANDIOKO": ["ERANDIO"],
    "GETARIAKO": ["GETARIA"],
    "GETXOKO": ["GETXO"],
    "GIPÚZKOA": ["GUIPÚZCOA"],
    "HERNANIKO": ["HERNANI"],
    "HIBAIKAKO": ["HIBAIKA"],
    "MUNDAKAKO": ["MUNDAKA"],
    "MUTRIKUKO": ["MUTRIKU"],
    "ONDARROAKO": ["ONDARROA"],
    "PASAIAKO": ["PASAIA"],
    "PLENTZIAKO": ["PLENTZIA"],
    "SANTURTZIKO": ["SANTURTZI"],
    "TOLOSALDEAKO": ["TOLOSALDEA"],
    "TRINTXERPEKO": ["TRINTXERPE"],
    "TXINGUDIKO": ["TXINGUDI"],
    "ZARAUZKO": ["ZARAUZ", "ZARAUTZ"],
    "ZUMAIAKO": ["ZUMAIA"],
}


_NORMALIZED_RACES = {
    "DONIBANE ZIBURUKO ESTROPADAK": [["SAN", "JUAN", "LUZ"]],
    "KEPA DEUN ARRANTZALEEN KOFRADÍA IKURRIÑA": [["COFRADÍA", "SAN", "PEDRO"], ["COFRADIA", "SAN", "PEDRO"]],
    "MEMORIAL LAGAR": [["MEMORIAL", "MIGUEL", "LORES"]],
    "MEMORIAL RULY": [["MEMORIAL", "RAUL", "REY"]],
    "BANDEIRA SALGADO CONGELADOS": [["SALGADO"]],
    "BANDEIRA CONCELLO DE RIBEIRA": [
        ["BANDEIRA", "RIBEIRA"],
        ["BANDEIRA", "RIVEIRA"],
        ["BANDERA", "RIBEIRA"],
        ["BANDERA", "RIVEIRA"],
    ],
    "BILBOKO BANDERA - BANDERA DE BILBAO": [["BILBOKO", "BANDERA"], ["BILBAO", "BANDERA"]],
    "BANDEIRA VIRXE DO CARME": [["VIRXE", "CARME"], ["VIRGEN", "CARMEN"]],
    "BANDEIRA ILLA DO SAMERTOLAMEU - FANDICOSTA": [["ILLA", "SAMERTOLAMEU", "FANDICOSTA"]],
}


def normalize_name_parts(name: str) -> list[tuple[str, int | None]]:
    """
    Normalize the name to a list of (name, edition)

    1. Remove parenthesis
    2. Add "CLASIFICATORIA" if it is a clasifier
    3. Split by " - " if not a play off
    4. Find multiple editions and try to split the name
    5. Find the edition
    6. Remove roman numbers
    """
    parts: list[tuple[str, int | None]] = []

    normalized = remove_parenthesis(whitespaces_clean(name))
    normalized = f"{normalized} ({'CLASIFICATORIA'})" if "CLASIFICATORIA" in name else normalized

    should_split = none(" - " in r in normalized for r in _NORMALIZED_RACES.keys())
    name_parts = normalized.split(" - ") if should_split and not is_play_off(normalized) else [normalized]
    if not is_play_off(normalized) and len(name_parts) == 1:
        editions = [w for w in normalized.split() if find_roman(w) is not None]
        if len(editions) > 1:
            name_parts = split_by_edition_parts(normalized, editions)

    for name in name_parts:
        edition = find_edition(name)
        clean_name = whitespaces_clean(remove_roman(name))
        parts.append((clean_name, edition))

    return parts


def normalize_race_name(name: str) -> str:
    """
    Normalize race name to a standard format

    1. Uppercase
    2. Remove acronyms
    3. Remove symbols
    4. Fix some known misspellings
    5. Remove league indicator
    6. Remove race sponsor
    7. Specific known race normalizations
    8. Specific known error names
    """
    name = whitespaces_clean(name).upper()
    name = deacronym_race_name(name)  # need to be executed before "." removal

    name = re.sub(r"[\'\".:ª]", " ", name)

    name = amend_race_name(name)
    name = remove_league_indicator(name)
    name = remove_race_sponsor(name)

    name = normalize_known_race_names(name)
    name = normalize_ko_race_names(name)

    return whitespaces_clean(name)


def find_edition(name: str) -> int | None:
    name = re.sub(r"[\'\".:]", " ", name)
    roman_options = [e for e in [find_roman(w) for w in name.split()] if e is not None]
    return roman_to_int(roman_options[0]) if roman_options else None


def split_by_edition_parts(normalized_name: str, editions: list[str]) -> list[str]:
    """
    Split the name by the edition numbers found in the name.

    examples:
        "XVII Bandera El Corte Inglés III Memorial Juan Zunzunegui"
        ["XVII Bandera El Corte Inglés", "III Memorial Juan Zunzunegui"]
    """
    name_parts = []
    if len(editions) > 1:
        previous_end_idx = 0
        for edition in editions:
            start_idx = normalized_name.find(edition, previous_end_idx)
            if start_idx > 0:
                name_parts.append(whitespaces_clean(normalized_name[previous_end_idx:start_idx]))
                previous_end_idx = start_idx
        name_parts.append(whitespaces_clean(normalized_name[previous_end_idx:]))
    return name_parts


def find_race_sponsor(name: str) -> str | None:
    """
    Find the race sponsor in our known list
    """
    for sponsor, _ in _KNOWN_RACE_SPONSORS:
        if sponsor in name:
            return sponsor
    return None


def remove_race_sponsor(name: str) -> str:
    for sponsor, should_replace in _KNOWN_RACE_SPONSORS:
        if not should_replace:
            continue
        name = name.replace(sponsor, "")
    if name.endswith(" - "):
        name = name.replace(" - ", "")
    return whitespaces_clean(name)


def remove_day_indicator(name: str) -> str:
    """
    Remove the day indicator from the name

    1. Remove "J" and the number
    2. Remove "JORNADA" and the number
    3. Remove "día" and the number
    3. Remove "XORNADA" and the number
    """
    name = re.sub(r"\(?(\dJ|J\d)\)?", "", name)  # found in some ACT races
    name = re.sub(r"\d+ª día|\d+ª DÍA|\(\d+ª? JORNADA\)", "", name)  # found in some ARC races
    name = re.sub(r"(XORNADA )\d+|\d+( XORNADA)", "", name)  # found in some LGT races
    return whitespaces_clean(name)


def remove_league_indicator(name: str) -> str:
    # ensure something remais after removing the league indicator
    for keyword_list in LEAGUE_KEYWORDS.values():
        for keyword in keyword_list:
            if keyword in name and len(name.replace(keyword, "").strip()) > 0:
                name = name.replace(keyword, "")

    return whitespaces_clean(remove_parenthesis(name))


def deacronym_race_name(name: str) -> str:
    name = re.sub(r"G\.? ?P\.?", "GRAN PREMIO", name)
    name = re.sub(r" T\.? ?J\.?", " TIERRA DE JÚBILO", name)
    name = re.sub(r"B\.? ", "BANDERA ", name)
    name = re.sub(r" SN ?", " SARI NAGUSIA ", name)
    name = re.sub(r"J\.? ?A\.? AGIRRE", "JOSE ANTONIO AGIRRE", name)

    return whitespaces_clean(name)


def amend_race_name(name: str) -> str:
    re.sub(r"(CONCELLO)( DE)?", "CONCELLO DE", name)
    name = name.replace("JESÚS TENORIO", "XESÚS TENORIO")
    name = name.replace("CCD CESANTES", "CESANTES")

    name = name.replace("/", "-").replace("-", " - ")
    name = apply_replaces(name, _MISSPELLINGS)
    return whitespaces_clean(name)


def normalize_known_race_names(name: str) -> str:
    edition = find_edition(name)
    normalized = match_normalization(name, _NORMALIZED_RACES)
    if edition and int_to_roman(edition) not in normalized.split():
        normalized = f"{int_to_roman(edition)} {normalized}"
    return normalized


def normalize_ko_race_names(name: str) -> str:
    name = " ".join([w if "HONDARRIBI" not in w else "HONDARRIBIKO" for w in name.split()])
    return apply_replaces(name, _KO_NAMES)
