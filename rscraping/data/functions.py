import csv
import os

from pyutils.strings import remove_symbols
from rscraping.data.models import Lineup, Race


def is_play_off(name: str) -> bool:
    return "PLAY" in name and "OFF" in name


def is_memorial(name: str) -> bool:
    return any(w in name for w in ["MEMORIAL", "OMEALDIA"])


def is_branch_club(name: str, letter: str = "B") -> bool:
    clean_name = remove_symbols(name)
    return any(e == letter for e in clean_name.upper().split())


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
