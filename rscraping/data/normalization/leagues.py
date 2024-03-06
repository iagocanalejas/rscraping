__LEAGUES_MAP = {
    "LIGA GALEGA DE TRAIÑAS": ["LGT"],
    "LIGA GALEGA DE TRAIÑAS A": ["LIGA A"],
    "LIGA GALEGA DE TRAIÑAS B": ["LIGA B"],
    "LIGA GALEGA DE TRAIÑAS FEMENINA": ["LIGA FEM", "LIGA F"],
    "EUSKO LABEL LIGA": ["ACT"],
}

__FEMALE_LEAGUES_MAP = {
    "LIGA GALEGA DE TRAIÑAS": ["LGT"],
    "LIGA GALEGA DE TRAIÑAS FEMENINA": ["LIGA FEM", "LIGA F"],
    "LIGA EUSKOTREN": ["ACT"],
}


def normalize_league_name(name: str, is_female: bool = False) -> str:
    """
    Normalize the league name to a standard name. Not female normalization also includes some female ones.

    1. Specific known league normalizations
    """
    leagues = __FEMALE_LEAGUES_MAP if is_female else __LEAGUES_MAP
    for k, v in leagues.items():
        if name in v:
            name = k
            break
    return name
