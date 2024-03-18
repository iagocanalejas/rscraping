import re

from pyutils.strings import remove_parenthesis, whitespaces_clean

# list of normalizations to specific to be generalized
_ENTITY_TITLES_SHORT = [
    "CR",
    "SD",
    "SDR",
    "CM",
    "CR",
    "AD",
    "CC",
    "CRC",
    "CDM",
    "CCD",
    "CRN",
    "CRO",
    "FEM",
    "B",
    "AN",
    "AE",
    "CN",
    "AR",
]
_ENTITY_TITLES = [
    "SOCIEDAD CULTURAL Y RECREATIVA",
    "BETERANOEN ARRAUNKETA KLUBA",
    "SOCIEDAD DEPORTIVA DE REMO",
    "CENTRO DEPORTIVO MARIÑEIRO",
    "CIRCULO CULTURAL DEPORTIVO",
    "CLUB DEPORTIVO DE REMO",
    "CLUB DE REMO NAUTICO",
    "ASOCIACIÓN DEPORTIVA",
    "SOCIEDAD DEPORTIVA",
    "CIRCULO CULTURAL",
    "CLUB DE REGATAS",
    "ARRAUN ELKARTEA",
    "ARRAUN LAGUNAK",
    "ARRAUN TALDEA",
    "CLUB ATLÉTICO",
    "CLUB NAUTICO",
    "CLUB DE REMO",
    "CLUB DO MAR",
    "CLUB DE MAR",
    "REMO CLUB",
    "CLUB REMO",
    "ARRAUN",
    "LICEO",
]
_NORMALIZED_ENTITIES = {
    "CABO DA CRUZ": ["CABO DE CRUZ", "CABO"],
    "ARES": ["DE ARES"],
    "CESANTES": ["CESANTES REMO - RODAVIGO"],
    "DEUSTO": ["DEUSTO - BILBAO", "DEUSTO-BILBAO"],
    "FEDERACION GALEGA DE REMO": ["LGT - FEGR"],
    "PERILLO": ["SALGADO PERILLO"],
    "LIGA GALEGA DE TRAIÑAS": ["LIGA GALEGA TRAIÑEIRAS", "LIGA GALEGA TRAINEIRAS", "LGT"],
    "BUEU": ["BUEU TECCARSA"],
    "ESTEIRANA": ["ESTEIRANA REMO"],
    "A CABANA": ["A CABANA FERROL"],
    "MUGARDOS - A CABANA": ["MUGARDOS - A CABANA FERROL"],
    "RIVEIRA": ["DE RIVEIRA"],
    "ZARAUTZ": ["ZARAUTZ GESALAGA-OKELAN", "ZARAUTZ INMOB. ORIO"],
    "PASAI DONIBANE KOXTAPE": ["P.DONIBANE IBERDROLA"],
    "HONDARRIBIA": ["HONADRRIBIA", "HONDARRBIA"],
    "SANTURTZI": ["ITSASOKO AMA", "SOTERA", "ITSASOKO AMA SANTURTZI"],
    "ONDARROA": ["OMDARROA"],
    "ILLUMBE": ["ILLUNBE"],
    "PORTUGALETE": ["POTUGALETE"],
    "GETXO": ["GETRXO"],
    "DONOSTIARRA": ["DNOSTIARRA"],
    "UR KIROLAK": ["UR-KIROLAK"],
    "URDAIBAI": ["BERMEO URDAIBAI"],
    "CASTREÑA": ["CASTRO CANTERAS DE SANTULLAN"],  # this one is a mess since SDR Castro close
}
_KNOWN_SPONSORS = [
    "BAHIAS DE BIZKAIA",
    "UROLA KOSTA",
    "PEREIRA",
    "MATRIX",
    "BIZKAIA",
    "FANDICOSTA",
    "CIKAUTXO",
    "ORIALKI",
    "AMENABAR",
    "ELECNOR",
    "BEREZ GALANTA",
    "JAMONES ANCIN",
    "NORTINDAL",
    "BERTAKO IGOGAILUAK",
    "GESALAGA OKELAN",
    "ANTTON BILBAO",
    "CMO VALVES",
    "RODAVIGO",
    "NORTEGAS",
    "SIMEI",
    "NATURHOUSE",
    "SALEGI JATETXEA",
]


def normalize_club_name(name: str) -> str:
    """
    Normalize a club name to a standard format

    1. Uppercase
    2. Remove parenthesis
    3. Remove acronyms
    4. Remove dots
    5. Remove club titles
    6. Remove club sponsors
    7. Specific known club normalizations
    """
    name = whitespaces_clean(remove_parenthesis(name.upper()))
    name = deacronym_club_name(name)

    name = name.replace(".", "")
    name = remove_club_title(name)
    name = remove_club_sponsor(name)

    # specific club normalizations
    for k, v in _NORMALIZED_ENTITIES.items():
        if name in v or any(part in name.split() for part in v):
            name = k
            break

    return whitespaces_clean(name)


def deacronym_club_name(name: str) -> str:
    if any(w in ["P", "D", "PD"] for w in name.split()):
        name = re.sub(r"P\.? ?D\.?", "PASAIA DONIBANE", name)
    if "CABANA" in name:
        name = name.replace("CABANA FERROL", "CABANA")
    return whitespaces_clean(name)


def remove_club_title(name: str) -> str:
    name = " ".join(w for w in name.split() if w not in _ENTITY_TITLES_SHORT)
    for title in _ENTITY_TITLES:
        if "DONOSTI" in name and title == "ARRAUN LAGUNAK":
            # edge case, need to avoid removing 'ARRAUN LAGUNAK' from 'DONOSTIA ARRAUN LAGUNAK'
            continue
        name = name.replace(title, "")
    return whitespaces_clean(name)


def remove_club_sponsor(name: str) -> str:
    for sponsor in _KNOWN_SPONSORS:
        name = name.replace(sponsor, "")
    if name.endswith(" - ") or name.startswith(" - "):
        name = name.replace(" - ", "")
    return whitespaces_clean(name)
