import re

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
    "CEFYCAL",
    "CONCELLO DE BOIRO",
    "FANDICOSTA",
    "ONURA HOMES",
    "SALGADO CONGELADOS",
    "SALGADO",
    "WOFCO",
    "YURRITA GROUP",
    "YURRITA",
]

_KO_NAMES = {
    "ALGORTAKO": ["ALGORTA"],
    "AREATAKO": ["AREATA"],
    "BERMEOKO": ["BERMEO"],
    "ELANTXOBEKO": ["ELANTXOBE"],
    "ERANDIOKO": ["ERANDIO"],
    "GETARIAKO": ["GETARIA"],
    "GETXOKO": ["GETXO"],
    "HERNANIKO": ["HERNANI"],
    "HIBAIKAKO": ["HIBAIKA"],
    "HONDARRIBIKO": ["HONDARRIBI", "HONDARRIBIA"],
    "MUNDAKAKO": ["MUNDAKA"],
    "MUTRIKUKO": ["MUTRIKU"],
    "ONDARROAKO": ["ONDARROA"],
    "PASAIAKO": ["PASAIA"],
    "PLENTZIAKO": ["PLENTZIA"],
    "SANTURTZIKO": ["SANTURTZI"],
    "TOLOSALDEAKO": ["TOLOSALDEA"],
    "TRINTXERPEKO": ["TRINTXERPE"],
    "TXINGUDIKO": ["TXINGUDI"],
    "ZARAUZKO": ["ZARAUZ"],
    "ZUMAIAKO": ["ZUMAIA"],
}


_NORMALIZED_RACES = {
    "DONIBANE ZIBURUKO ESTROPADAK": [["SAN", "JUAN", "LUZ"]],
    "KEPA DEUN ARRANTZALEEN KOFRADÍA IKURRIÑA": [["COFRADÍA", "SAN", "PEDRO"], ["COFRADIA", "SAN", "PEDRO"]],
    "MEMORIAL LAGAR": [["MEMORIAL", "MIGUEL", "LORES"]],
    "MEMORIAL RULY": [["MEMORIAL", "RAUL", "REY"]],
}


def normalize_name_parts(normalized_name: str) -> list[tuple[str, int | None]]:
    """
    Normalize the name to a list of (name, edition)

    1. Remove parenthesis
    2. Add "CLASIFICATORIA" if it is a clasifier
    3. Split by " - " if not a play off
    4. Find the edition
    5. Remove roman numbers
    """
    parts: list[tuple[str, int | None]] = []
    is_clasifier = "CLASIFICATORIA" in normalized_name
    normalized_name = remove_parenthesis(whitespaces_clean(normalized_name))
    normalized_name = f"{normalized_name} ({'CLASIFICATORIA'})" if is_clasifier else normalized_name
    name_parts = normalized_name.split(" - ") if not is_play_off(normalized_name) else [normalized_name]

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


def find_race_sponsor(name: str) -> str | None:
    """
    Find the race sponsor in our known list
    """
    for sponsor in _KNOWN_RACE_SPONSORS:
        if sponsor in name:
            return sponsor
    return None


def remove_race_sponsor(name: str) -> str:
    for sponsor in _KNOWN_RACE_SPONSORS:
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
    words = name.split()
    filtered_words = [w for w in words if w not in {"B", "F"}]

    if name.endswith(" A"):
        filtered_words = filtered_words[:-1]

    return whitespaces_clean(" ".join(filtered_words))


def deacronym_race_name(name: str) -> str:
    name = re.sub(r"G\.? ?P\.?", "GRAN PREMIO", name)
    name = re.sub(r" T\.? ?J\.?", " TIERRA DE JÚBILO", name)
    name = re.sub(r"B\.? ", "BANDERA ", name)
    name = re.sub(r" SN ?", " SARI NAGUSIA ", name)
    name = re.sub(r"J\.? ?A\.? AGIRRE", "JOSE ANTONIO AGIRRE", name)

    return whitespaces_clean(name)


def amend_race_name(name: str) -> str:
    re.sub(r"(CONCELLO)( DE)?", "CONCELLO DE", name)
    name = name.replace("BILBOKO BANDERA - BANDERA DE BILBAO", "BANDERA DE BILBAO")
    name = name.replace("JESÚS TENORIO", "XESÚS TENORIO")
    name = name.replace("CCD CESANTES", "CESANTES")

    name = name.replace("/", "-").replace("-", " - ")
    for a, b in _MISSPELLINGS:
        name = name.replace(a, b)
    return whitespaces_clean(name)


def normalize_known_race_names(name: str) -> str:
    for synonym, values in _NORMALIZED_RACES.items():
        for value in values:
            if name in " ".join(value) or all(v in name for v in value):
                return synonym
    return name


def normalize_ko_race_names(name: str) -> str:
    for k, values in _KO_NAMES.items():
        if any(v in name for v in values) and k not in name:
            for v in values:
                name = name.replace(v, k)
            return name
    return name
