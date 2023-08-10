import re
from typing import List, Optional, Tuple

from pyutils.strings import find_roman, remove_parenthesis, remove_roman, roman_to_int, whitespaces_clean
from rscraping.data.functions import is_play_off

_MISSPELLINGS = [
    ("IKURIÑA", "IKURRIÑA"),
    ("IKURINA", "IKURRIÑA"),
    ("IÑURRIÑA", "IKURRIÑA"),
    ("KOFRADIA", "KOFRADÍA"),
    ("RECICLAMOS LA LUZ", ""),
    ("PIRATA COM", "PIRATA.COM"),
    ("PAY OFF", "PlAY OFF"),
    ("CASTILLA - LA", "CASTILLA LA"),
    ("AYTO", "AYUNTAMIENTO"),
    (" AE ", ""),
    ("EXCMO", ""),
    ("ILTMO", ""),
    ("TRAIEIRAS", "TRAIÑEIRAS"),
]

_KNOWN_RACE_SPONSORS = [
    "ONURA HOMES",
    "YURRITA GROUP",
    "WOFCO",
    "SALGADO",
    "CEFYCAL",
    "CONCELLO DE BOIRO",
]


def normalize_name_parts(normalized_name: str) -> List[Tuple[str, Optional[int]]]:
    parts: List[Tuple[str, Optional[int]]] = []
    normalized_name = remove_parenthesis(whitespaces_clean(normalized_name))
    name_parts = normalized_name.split(" - ") if not is_play_off(normalized_name) else [normalized_name]

    for name in name_parts:
        edition = find_edition(name)
        clean_name = whitespaces_clean(remove_roman(name))
        parts.append((clean_name, edition))

    return parts


def normalize_race_name(name: str) -> str:
    name = whitespaces_clean(name).upper()
    name = re.sub(r"[\'\".:ª]", " ", name)

    name = amend_race_name(name)
    name = deacronym_race_name(name)
    name = remove_league_indicator(name)
    name = remove_race_sponsor(name)

    return whitespaces_clean(name)


def remove_league_indicator(name: str) -> str:
    words = name.split()
    filtered_words = [w for w in words if w not in {"B", "F"}]

    if name.endswith(" A"):
        filtered_words = filtered_words[:-1]

    return whitespaces_clean(" ".join(filtered_words))


def remove_race_sponsor(name: str) -> str:
    for sponsor in _KNOWN_RACE_SPONSORS:
        name = name.replace(sponsor, "")
    if name.endswith(" - "):
        name = name.replace(" - ", "")
    return whitespaces_clean(name)


def remove_day_indicator(name: str) -> str:
    name = re.sub(r"\(?(\dJ|J\d)\)?", "", name)  # found in some ACT races
    name = re.sub(r"\d+ª día|\(\d+ª? JORNADA\)", "", name)  # found in some ARC races
    name = re.sub(r"(XORNADA )\d+|\d+( XORNADA)", "", name)  # found in some LGT races
    return whitespaces_clean(name)


def find_race_sponsor(name: str) -> Optional[str]:
    for sponsor in _KNOWN_RACE_SPONSORS:
        if sponsor in name:
            return sponsor
    return None


def find_edition(name: str) -> Optional[int]:
    name = re.sub(r"[\'\".:]", " ", name)
    roman_options = [e for e in [find_roman(w) for w in name.split()] if e is not None]
    return roman_to_int(roman_options[0]) if roman_options else None


def deacronym_race_name(name: str) -> str:
    name = re.sub(r"G\.? ?P\.?", "GRAN PREMIO", name)
    name = re.sub(r" T\.? ?J\.?", " TIERRA DE JÚBILO", name)
    name = re.sub(r"B\.? ", "BANDERA ", name)
    name = re.sub(r" SN ?", " SARI NAGUSIA ", name)
    name = re.sub(r"J\.? ?A\.? AGIRRE", "JOSE ANTONIO AGIRRE", name)
    name = name.replace("BILBOKO BANDERA - BANDERA DE BILBAO", "BANDERA DE BILBAO")

    return whitespaces_clean(name)


def amend_race_name(name: str) -> str:
    re.sub(r"(CONCELLO)( DE)?", "CONCELLO DE", name)

    name = name.replace("/", "-").replace("-", " - ")
    for a, b in _MISSPELLINGS:
        name = name.replace(a, b)
    return whitespaces_clean(name)
