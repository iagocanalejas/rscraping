from datetime import date

from pyutils.strings import remove_symbols
from rscraping.data.constants import SYNONYM_FEMALE, SYNONYM_MEMORIAL, SYNONYMS


def should_be_time_trial(name: str, date: date) -> bool:
    return is_play_off(name) or (all(w in name.split() for w in ["TERESA", "HERRERA"]) and date.isoweekday() == 6)


def is_play_off(name: str) -> bool:
    return "PLAY" in name and "OFF" in name


def is_memorial(name: str) -> bool:
    return any(w in name.split() for w in SYNONYMS[SYNONYM_MEMORIAL])


def is_female(name: str) -> bool:
    return any(w in name.split() for w in SYNONYMS[SYNONYM_FEMALE])


def is_branch_club(name: str, letter: str = "B") -> bool:
    clean_name = remove_symbols(name)
    return any(e == letter for e in clean_name.upper().split())


def is_act(name: str, is_female: bool = False) -> bool:
    if is_female:
        return "EUSKOTREN" in name
    return all(w in name.split() for w in ["EUSKO", "LABEL"]) or "ACT" in name.split() or "EUSKOLABEL" in name


def is_lgt(name: str, letter: str = "A") -> bool:
    match letter:
        case "A":
            return all(w in name.split() for w in ["LGT", "A"]) or "LGTA" in name
        case "B":
            return all(w in name.split() for w in ["LGT", "B"]) or "LGTB" in name
        case "F":
            return all(w in name.split() for w in ["LGT", "F"]) or "LGTF" in name
    raise ValueError(f"Invalid letter: {letter}")


def is_arc(name: str, category: int = 1) -> bool:
    match category:
        case 1:
            return "ARC" in name.split()
        case 2:
            return "ARC2" in name.split()
    raise ValueError(f"Invalid category: {category}")


def is_ete(name: str) -> bool:
    return "ETE" in name.split()
