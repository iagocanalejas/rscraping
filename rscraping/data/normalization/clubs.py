import re

from pyutils.strings import (
    CONJUNCTIONS,
    match_normalization,
    remove_parenthesis,
    whitespaces_clean,
)
from rscraping.data.checks import is_branch_club
from rscraping.data.models import Race

_ENTITY_TITLES_SHORT = [
    "AD",
    "AE",
    "AN",
    "AR",
    "AT",
    "CCD",
    "CDM",
    "CRC",
    "CRN",
    "CRO",
    "CC",
    "CM",
    "CR",
    "CN",
    "CD",
    "CP",
    "ED",
    "FEM",
    "RC",
    "SDR",
    "SD",
    "SR",
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
    "TRAINERA DE",  # this will convert 'TRAINERA DE SAN JUAN' to 'SAN JUAN' matching the old town boats into club ones
    "ARRAUN",
    "LICEO DE",
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
    "UR KIROLAK": [["UR", "KIROLAK"]],
    "URDAIBAI": [["BERMEO", "URDAIBAI"]],
}

_KNOWN_SPONSORS = [
    "AMENABAR",
    "ANTTON BILBAO",
    "AVIA",
    "BABYAUTO",
    "BAHIAS DE BIZKAIA",
    "BEREZ GALANTA",
    "BERTAKO IGOGAILUAK",
    "BIZKAIA",
    "CANTERAS DE SANTULLAN",
    "CIKAUTXO",
    "CMO VALVES",
    "DELTECO",
    "ELECNOR",
    "FANDICOSTA",
    "GESALAGA OKELAN",
    "GLASS",
    "GO FIT",
    "IBERIA",
    "IBERDROLA",
    "JAMONES ANCIN",
    "MATRIX",
    "MICHELIN",
    "MITXELENA MEKANIZATUAK",
    "NATURHOUSE",
    "NORTEGAS",
    "NORTINDAL",
    "OCCIDENT",
    "ORIALKI",
    "PEREIRA",
    "RODAVIGO",
    "SALEGI JATETXEA",
    "SIMEI",
    "SUSPERREGI EDUKIONTZIAK",
    "TECCARSA",
    "UROLA KOSTA",
    "ÉNERYT SERVICIOS",
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
    7. Remove remaining conjunctions at the beginning
    8. Specific known club normalizations
    """
    name = whitespaces_clean(remove_parenthesis(name.upper()))
    name = deacronym_club_name(name)

    name = name.replace(".", "")
    name = remove_club_title(name)
    name = remove_club_sponsor(name)

    name = " ".join(name.split()[1:]) if name.split() and name.split()[0] in CONJUNCTIONS else name

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
        if "DONOSTI" in name and (title == "ARRAUN LAGUNAK" or title == "ARRAUN") or name == "ARRAUN LAGUNAK":
            # edge case, need to avoid removing 'ARRAUN LAGUNAK' from 'DONOSTIA ARRAUN LAGUNAK'
            continue
        name = name.replace(title, "")
    return whitespaces_clean(name)


def remove_club_sponsor(name: str) -> str:
    for sponsor in _KNOWN_SPONSORS:
        if name.replace(sponsor, "") not in ["", " B", " C"]:  # avoid removing the whole name
            name = name.replace(sponsor, "")
    name = whitespaces_clean(name.replace("-", " - "))
    if name.endswith(" -") or name.startswith("- "):
        name = name.replace("-", "")
    return whitespaces_clean(name)


def ensure_b_teams_have_the_main_team_racing(race: Race):
    """
    Ensure that if a B team is racing, the main team is also racing
    """
    for i, p in enumerate(race.participants):
        if is_branch_club(p.participant) or is_branch_club(p.participant, letter="C"):
            main_team = p.participant.rstrip(" B").rstrip(" C")
            if not any(p2.participant == main_team for p2 in race.participants):
                race.participants[i].participant = main_team
