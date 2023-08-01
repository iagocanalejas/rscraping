import logging
import re
from typing import Optional

from pyutils.strings import whitespaces_clean
from unidecode import unidecode

logger = logging.getLogger(__name__)

_NORMALIZED_MALE_RACES = {
    "ZARAUZKO IKURRIÑA": ["ZARAUZKO ESTROPADAK", "ZARAUZKO IKURRIÑA"],
    "HONDARRIBIKO IKURRIÑA": ["HONDARRIBIKO IKURRIÑA", "HONDARRIBIKO BANDERA"],
    "EL CORREO IKURRIÑA": ["EL CORREO IKURRIÑA", "IKURRIÑA EL CORREO"],
    "GRAN PREMIO EL CORTE INGLÉS": ["EL CORTE"],
    "BANDERA MARINA DE CUDEYO": ["MARINA CUDEYO", "MARINA DE CUDEYO"],
    "GRAN PREMIO FANDICOSTA": ["GRAN PREMIO FANDICOSTA", "GP FANDICOSTA"],
    "BANDEIRA CIDADE DE FERROL": ["MIGUEL DERUNGS"],
    "BANDEIRA OUTÓN Y FERNÁNDEZ": ["OUTÓN Y FERNÁNDEZ", "OUTÓN FERNÁNDEZ", "OUTON FERNÁNDEZ"],
    "DONIBANE ZIBURUKO ESTROPADAK": ["DONIBANE ZIBURUKONESTROPADA"],
}

_NORMALIZED_FEMALE_RACES = {
    "GRAN PREMIO FANDICOSTA FEMININO": ["GRAN PREMIO FANDICOSTA", "GP FANDICOSTA"],
    "BANDEIRA FEMININA CIDADE DE FERROL": ["MIGUEL DERUNGS"],
}

_MISSPELLINGS = [
    ("IKURIÑA", "IKURRIÑA"),
    ("KOFRADIA", "KOFRADÍA"),
    ("RECICLAMOS LA LUZ", ""),
    ("PIRATA COM", "PIRATA.COM"),
    ("PAY OFF", "PlAY OFF"),
]

_KNOWN_RACE_SPONSORS = [
    "ONURA HOMES",
    "YURRITA GROUP",
]


def normalize_race_name(name: str, is_female: bool) -> str:
    name = whitespaces_clean(name).upper()
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


def deacronym_race_name(name: str) -> str:
    name = re.sub(r"G\.? ?P\.?", "GRAN PREMIO", name)
    name = re.sub(r" T\.? ?J\.?", " TIERRA DE JÚBILO", name)
    name = re.sub(r"B\.? ", "BANDERA ", name)

    return whitespaces_clean(name)


def amend_race_name(name: str) -> str:
    name = re.sub(r"[\'\".:ª]", " ", name)
    re.sub(r"(CONCELLO)( DE)?", "CONCELLO DE", name)

    name = name.replace("-", " - ")
    for a, b in _MISSPELLINGS:
        name = name.replace(a, b)
    return whitespaces_clean(name)
