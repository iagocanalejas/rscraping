import re

from pyutils.strings import match_normalization, remove_parenthesis, whitespaces_clean
from rscraping.data.checks import is_branch_club

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
    "PUEBLA - CABO": [["CABO", "PUEBLA"]],
    "CABO DA CRUZ": [["CABO", "CRUZ"], ["CABO"]],
    "ARES": [["DE", "ARES"]],
    "DEUSTO": [["DEUSTO", "BILBAO"]],
    "FEDERACION GALEGA DE REMO": [["LGT", "FEGR"]],
    "PERILLO": [["SALGADO", "PERILLO"]],
    "LIGA GALEGA DE TRAIÑAS": [
        ["LIGA", "GALEGA", "TRAIÑEIRAS"],
        ["LIGA", "GALEGA", "TRAINEIRAS"],
        ["LGT"],
    ],
    "ESTEIRANA": [["ESTEIRANA", "REMO"]],
    "MUGARDOS - A CABANA": [["MUGARDOS", "CABANA", "FERROL"]],
    "A CABANA": [["CABANA", "FERROL"]],
    "RIVEIRA": [[" RIVEIRA"]],
    "ZARAUTZ": [
        ["ZARAUTZ", "GESALAGA", "OKELAN"],
        ["ZARAUTZ", "INMOB", "ORIO"],
    ],
    "PASAI DONIBANE KOXTAPE": [["DONIBANE", "IBERDROLA"], ["KOXTAPE"]],
    "HONDARRIBIA": [["HONADRRIBIA"], ["HONDARRBIA"]],
    "SANTURTZI": [
        ["ITSASOKO", "AMA"],
        ["SOTERA"],
    ],
    "ONDARROA": [["OMDARROA"]],
    "ILLUMBE": [["ILLUNBE"]],
    "PORTUGALETE": [["POTUGALETE"]],
    "GETXO": [["GETRXO"]],
    "DONOSTIARRA": [["DNOSTIARRA"]],
    "UR KIROLAK": [["UR-KIROLAK"]],
    "URDAIBAI": [["BERMEO", "URDAIBAI"]],
    "CASTREÑA": [["CASTRO", "CANTERAS", "SANTULLAN"]],  # this one is a mess since SDR Castro close
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
    "TECCARSA",
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

    is_B_team, is_C_team = is_branch_club(name), is_branch_club(name, letter="C")  # never saw more than a C
    name = match_normalization(name, _NORMALIZED_ENTITIES)
    name = f"{name} C" if is_C_team and not is_branch_club(name, letter="C") else name
    name = f"{name} B" if is_B_team and not is_branch_club(name) else name

    return whitespaces_clean(name)


def deacronym_club_name(name: str) -> str:
    if any(w in ["P", "D", "PD"] for w in name.split()):
        name = re.sub(r"P\.? ?D\.?", "PASAIA DONIBANE", name)
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
