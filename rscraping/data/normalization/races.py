import logging
import re
from typing import List, Optional, Tuple

from pyutils.strings import find_roman, remove_parenthesis, remove_roman, roman_to_int, whitespaces_clean
from unidecode import unidecode

logger = logging.getLogger(__name__)

_NORMALIZED_MALE_RACES = {
    "ZARAUZKO IKURRIÑA": ["ZARAUZKO ESTROPADAK", "ZARAUZKO IKURRIÑA"],
    "HONDARRIBIKO IKURRIÑA": ["HONDARRIBIKO IKURRIÑA", "HONDARRIBIKO BANDERA"],
    "GRAN PREMIO EL CORTE INGLÉS": ["EL CORTE"],
    "BANDERA MARINA DE CUDEYO": ["MARINA CUDEYO", "MARINA DE CUDEYO"],
    "GRAN PREMIO FANDICOSTA": ["GRAN PREMIO FANDICOSTA", "GP FANDICOSTA"],
    "BANDEIRA CIDADE DE FERROL": ["MIGUEL DERUNGS"],
    "BANDEIRA OUTÓN Y FERNÁNDEZ": ["OUTÓN Y FERNÁNDEZ", "OUTÓN FERNÁNDEZ", "OUTON FERNÁNDEZ"],
    "DONIBANE ZIBURUKO ESTROPADAK": ["DONIBANE ZIBURUKONESTROPADA"],
    "BANDERA DE BILBAO": ["BILBOKO BANDERA"],
}

_NORMALIZED_FEMALE_RACES = {
    "GRAN PREMIO FANDICOSTA FEMININO": ["GRAN PREMIO FANDICOSTA", "GP FANDICOSTA"],
    "BANDEIRA FEMININA CIDADE DE FERROL": ["MIGUEL DERUNGS"],
}

_MISSPELLINGS = [
    ("IKURIÑA", "IKURRIÑA"),
    ("IKURINA", "IKURRIÑA"),
    ("KOFRADIA", "KOFRADÍA"),
    ("RECICLAMOS LA LUZ", ""),
    ("PIRATA COM", "PIRATA.COM"),
    ("PAY OFF", "PlAY OFF"),
    ("CASTILLA - LA", "CASTILLA LA"),
    ("AYTO", "AYUNTAMIENTO"),
    (" AE ", ""),
    ("EXCMO", ""),
    ("ILTMO", ""),
]

_KNOWN_RACE_SPONSORS = [
    "ONURA HOMES",
    "YURRITA GROUP",
    "WOFCO",
]


def normalize_name_parts(normalized_name: str) -> List[Tuple[str, Optional[int]]]:
    parts: List[Tuple[str, Optional[int]]] = []
    normalized_name = remove_parenthesis(whitespaces_clean(normalized_name))
    name_parts = normalized_name.split(" - ")

    for name in name_parts:
        edition = find_edition(name)
        clean_name = remove_roman(name)
        parts.append((clean_name, edition))

    return parts


def normalize_race_name(name: str, is_female: bool) -> str:
    name = whitespaces_clean(name).upper()
    name = re.sub(r"[\'\".:ª]", " ", name)

    name = amend_race_name(name)
    name = deacronym_race_name(name)
    name = remove_league_indicator(name)
    name = remove_race_sponsor(name)

    normalizations = _NORMALIZED_FEMALE_RACES if is_female else _NORMALIZED_MALE_RACES
    # specific race normalizations
    for k, v in normalizations.items():
        if name in v or any(part in name for part in v):
            name = k
            break

    return whitespaces_clean(name)


def remove_league_indicator(name: str) -> str:
    words = name.split()
    filtered_words = [w for w in words if w not in {"B", "F"}]

    if name.endswith(" A"):
        filtered_words = filtered_words[:-1]

    return " ".join(filtered_words)


def remove_race_sponsor(name: str) -> str:
    for sponsor in _KNOWN_RACE_SPONSORS:
        name = name.replace(sponsor, "")
        name = name.replace(unidecode(sponsor), "")
    if name.endswith(" - "):
        name = name.replace(" - ", "")
    return whitespaces_clean(name)


def find_race_sponsor(name: str) -> Optional[str]:
    for sponsor in _KNOWN_RACE_SPONSORS:
        if sponsor in name:
            return sponsor
    return None


def find_edition(name: str) -> Optional[int]:
    name = re.sub(r"[\'\".:]", " ", name)
    roman_options = list(filter(None, [find_roman(w) for w in name.split()]))
    return roman_to_int(roman_options[0]) if roman_options else None


def deacronym_race_name(name: str) -> str:
    name = re.sub(r"G\.? ?P\.?", "GRAN PREMIO", name)
    name = re.sub(r" T\.? ?J\.?", " TIERRA DE JÚBILO", name)
    name = re.sub(r"B\.? ", "BANDERA ", name)
    name = re.sub(r" SN ?", " SARI NAGUSIA ", name)
    name = re.sub(r"J\.? ?A\.? AGIRRE", "JOSE ANTONIO AGIRRE", name)

    return whitespaces_clean(name)


def amend_race_name(name: str) -> str:
    re.sub(r"(CONCELLO)( DE)?", "CONCELLO DE", name)

    name = name.replace("/", "-").replace("-", " - ")
    for a, b in _MISSPELLINGS:
        name = name.replace(a, b)
    return whitespaces_clean(name)
