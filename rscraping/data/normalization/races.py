import logging
import re

from pyutils.strings import whitespaces_clean

logger = logging.getLogger(__name__)

__NORMALIZED_MALE_RACES = {
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

__NORMALIZED_FEMALE_RACES = {
    "GRAN PREMIO FANDICOSTA FEMININO": ["GRAN PREMIO FANDICOSTA", "GP FANDICOSTA"],
    "BANDEIRA FEMININA CIDADE DE FERROL": ["MIGUEL DERUNGS"],
}

__MISSPELLINGS = [
    ("IKURIÑA", "IKURRIÑA"),
    ("KOFRADIA", "KOFRADÍA"),
    ("RECICLAMOS LA LUZ", ""),
    ("PIRATA COM", "PIRATA.COM"),
    ("PAY OFF", "PlAY OFF"),
]


def normalize_race_name(name: str, is_female: bool) -> str:
    name = whitespaces_clean(name).upper()
    name = amend_race_name(name)
    name = deacronym_race_name(name)
    name = remove_league_indicator(name)

    normalizations = __NORMALIZED_FEMALE_RACES if is_female else __NORMALIZED_MALE_RACES
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


def deacronym_race_name(name: str) -> str:
    name = re.sub(r"G\.? ?P\.?", "GRAN PREMIO", name)
    name = re.sub(r" T\.? ?J\.?", " TIERRA DE JÚBILO", name)
    name = re.sub(r"B\.? ", "BANDERA ", name)

    return whitespaces_clean(name)


def amend_race_name(name: str) -> str:
    name = re.sub(r"[\'\".:ª]", " ", name)
    re.sub(r"(CONCELLO)( DE)?", "CONCELLO DE", name)

    name = name.replace("-", " - ")
    for a, b in __MISSPELLINGS:
        name = name.replace(a, b)
    return whitespaces_clean(name)
