from pyutils.strings import whitespaces_clean

_NORMALIZED_TOWNS = {
    "VILAGARCÍA": ["VILAXOAN", "VILAXOÁN"],
    "DONOSTI": ["SAN SEBATIÁN", "SAN SEBASTIAN"],
    "PASAIA": ["PASAI DONIBADE", "PASAI SAN JUAN", "PASAI SAN PEDRO", "SAN JUAN", "SAN PEDRO"],
}

_PROVINCES = [
    "A CORUÑA",
    "PONTEVEDRA",
    "GIPUZKOA",
    "BIZKAIA",
    "CANTABRIA",
]


def normalize_town(town: str) -> str:
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
