import re

from pyutils.strings import remove_parenthesis, whitespaces_clean

_NORMALIZED_TOWNS = {
    "VILAGARCÍA": ["VILAXOAN", "VILAXOÁN"],
    "DONOSTI": ["SAN SEBATIÁN", "SAN SEBASTIAN", "DONOSTIA"],
    "PASAIA": ["PASAI DONIBANE", "PASAI SAN JUAN", "PASAI SAN PEDRO", "SAN JUAN", "SAN PEDRO"],
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
    for k, v in _NORMALIZED_TOWNS.items():
        if town in v or any(part in town.split() for part in v):
            town = k
            break
    return whitespaces_clean(town)


def extract_town(name: str) -> str | None:
    """
    Extract the town from the name

    1. Try to extract the town from the parenthesis
    2. Try to extract the town from the 'CONCELLO DE' part
    """

    def validate_town(town: str) -> str | None:
        if town not in ["CLASIFICATORIA"]:
            return town
        return None

    town = None
    matches = re.findall(r"\((.*?)\)", name)
    if matches:
        town = validate_town(whitespaces_clean(matches[0]).upper())

    if not town and "CONCELLO DE" in name:
        town = validate_town(whitespaces_clean(remove_parenthesis(name.split("CONCELLO DE ")[1])).upper())

    return town
