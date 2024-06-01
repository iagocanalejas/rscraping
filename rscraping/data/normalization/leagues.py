from pyutils.strings import match_normalization
from rscraping.data.checks import is_act, is_arc, is_ete, is_lgt, is_play_off

__LEAGUES_MAP = {
    "LIGA GALEGA DE TRAIÑAS": [["LGT"]],
    "LIGA GALEGA DE TRAIÑAS A": [["LIGA", "A"]],
    "LIGA GALEGA DE TRAIÑAS B": [["LIGA", "B"]],
    "LIGA GALEGA DE TRAIÑAS FEMENINA": [["LIGA", "FEM"], ["LIGA", "F"]],
    "EUSKO LABEL LIGA": [["ACT"]],
}

__FEMALE_LEAGUES_MAP = {
    "LIGA GALEGA DE TRAIÑAS": [["LGT"]],
    "LIGA GALEGA DE TRAIÑAS FEMENINA": [["LIGA", "FEM"], ["LIGA", "F"]],
    "LIGA EUSKOTREN": [["ACT"]],
}


def normalize_league_name(name: str, is_female: bool = False) -> str:
    """
    Normalize the league name to a standard name. Not female normalization also includes some female ones.

    1. Specific known league normalizations
    """
    leagues = __FEMALE_LEAGUES_MAP if is_female else __LEAGUES_MAP
    return match_normalization(name, leagues)


def find_league(name: str) -> str | None:
    """
    Find the league of a competition by its name.

    1. Play-offs
    2. Leagues
    """
    if is_play_off(name):
        if is_act(name) or is_act(name, is_female=True) or ("ARC" in name and "LGT" in name):
            return "ACT"
        if is_lgt(name):
            return "LGT"
        if is_arc(name):
            return "ARC"
        return None

    if is_lgt(name, "A"):
        return "LIGA A"
    if is_lgt(name, "B"):
        return "LIGA B"
    if is_lgt(name, "F"):
        return "LIGA FEM"
    if is_act(name):
        return "EUSKO LABEL LIGA"
    if is_act(name, is_female=True):
        return "LIGA EUSKOTREN"
    if is_arc(name, category=2):
        return "ASOCIACIÓN DE REMO DEL CANTÁBRICO 2"
    if is_arc(name):
        return "ASOCIACIÓN DE REMO DEL CANTÁBRICO 1"
    if is_ete(name):
        return "EMAKUMEZKO TRAINERUEN ELKARTEA"
    return None
