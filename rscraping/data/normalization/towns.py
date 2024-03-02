import re

from pyutils.strings import (
    match_normalization,
    remove_parenthesis,
    whitespaces_clean,
)
from rscraping.data.constants import SYNONYM_PORT, SYNONYMS

_NORMALIZED_TOWNS = {
    "VILAGARCÍA": [
        ["VILAXOAN"],
        ["VILAXOÁN"],
        ["VILAGARCIA"],
    ],
    "DONOSTI": [
        ["SAN", "SEBASTIAN"],
        ["SAN", "SEBASTIÁN"],
        ["DONOSTIA"],
    ],
    "PASAIA": [
        ["PASAI", "DONIBANE"],
        ["PASAI", "SAN", "JUAN"],
        ["PASAI", "SAN", "PEDRO"],
        ["SAN", "JUAN"],
        ["SAN", "PEDRO"],
    ],
    "REDONDELA": [
        ["CHAPELA"],
        ["CESANTES"],
    ],
    "FERROL": [["CABANA"]],
    "A CORUÑA": [["ORZAN"]],
    "A POBRA DO CARAMIÑAL": [["POBRA"], ["PUEBLA"]],
    "MOAÑA": [
        ["MEIRA"],
        ["TIRAN"],
        ["TIRÁN"],
    ],
    "BOIRO": [["CABO", "CRUZ"]],
    "OLEIROS": [["PERILLO"]],
    "O GROVE": [
        ["PEDRAS", "NEGRAS"],
        ["GROVE"],
    ],
}

_PROVINCES = [
    "A CORUÑA",
    "PONTEVEDRA",
    "GIPUZKOA",
    "BIZKAIA",
    "CANTABRIA",
]


def normalize_town(town: str) -> str:
    """
    Normalize a town name to a standard format

    1. Uppercase
    2. Remove "PORTO DE"
    2. Remove province
    3. Specific known town normalizations
    """
    town = whitespaces_clean(town.upper().replace("PORTO DE ", ""))

    town = remove_province(town)
    town = amend_town(town)

    return town


def remove_province(town: str) -> str:
    for p in _PROVINCES:
        if p in town:
            maybe_town = whitespaces_clean(town.replace(p, ""))
            if maybe_town:
                town = maybe_town
    return town


def amend_town(town: str) -> str:
    town = town.replace("/", "-").replace("-", " - ")

    for w in SYNONYMS[SYNONYM_PORT]:
        town = town.replace(f"{w} DE", "").replace(f"{w} DA", "").replace(w, "")

    town = match_normalization(town, _NORMALIZED_TOWNS)
    return whitespaces_clean(town)


def extract_town(name: str) -> str | None:
    """
    Extract the town from the name

    1. Try to extract the town from the parenthesis
    2. Try to extract the town from the 'CONCELLO DE' part
    """

    town = None
    matches = re.findall(r"\((.*?)\)", name)
    if matches:
        town = whitespaces_clean(matches[0]).upper()

    if not town and "CONCELLO DE" in name:
        town = whitespaces_clean(remove_parenthesis(name.split("CONCELLO DE ")[1])).upper()

    return town if town not in ["CLASIFICATORIA"] else None
