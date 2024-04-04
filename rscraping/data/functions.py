import csv
import os
import sys
from typing import Any

from pyutils.strings import remove_symbols
from rscraping.data.constants import SYNONYM_FEMALE, SYNONYM_MEMORIAL, SYNONYMS
from rscraping.data.models import Lineup, Race


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


def expand_path(path: str, valid_files: list[str]) -> list[str]:
    def is_valid(file: str) -> bool:
        _, extension = os.path.splitext(file)
        return extension.upper() in valid_files

    files = [os.path.join(path, file) for file in os.listdir(path)] if os.path.isdir(path) else [path]
    return [f for f in files if is_valid(f)]


def save_csv(lineups: list[Race] | list[Lineup], file_name: str):
    if not len(lineups):
        return

    file_name = file_name if ".csv" in file_name else f"{file_name}.csv"
    with open(file_name, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(lineups[0].__dict__.keys())  # write headers
        for item in lineups:
            writer.writerow(item.__dict__.values())


def sys_print_items(items: list[Any]):
    items_len = len(items)
    sys.stdout.write("[")
    for i, race in enumerate(items):
        sys.stdout.write(str(race))
        if i != items_len - 1:
            sys.stdout.write(",")
    sys.stdout.write("]\n")
    sys.stdout.flush()
