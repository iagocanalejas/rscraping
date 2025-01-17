import csv
import os
import sys
from typing import Any

from rscraping.data.models import Race


def expand_path(
    path: str, valid_files: list[str]
) -> list[str]:  # pragma: no cover - util functions not needing testing
    def is_valid(file: str) -> bool:
        _, extension = os.path.splitext(file)
        return extension.upper() in valid_files

    files = [os.path.join(path, file) for file in os.listdir(path)] if os.path.isdir(path) else [path]
    return [f for f in files if is_valid(f)]


def save_csv(items: list[Race], file_name: str):  # pragma: no cover - util functions not needing testing
    assert len(items), "no items to save"

    file_name = file_name if ".csv" in file_name else f"{file_name}.csv"
    with open(file_name, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(items[0].__dict__.keys())  # write headers
        for item in items:
            writer.writerow(item.__dict__.values())


def sys_print_items(items: list[Any]):  # pragma: no cover - util functions not needing testing
    items_len = len(items)
    sys.stdout.write("[")
    for i, race in enumerate(items):
        sys.stdout.write(str(race))
        if i != items_len - 1:
            sys.stdout.write(",")
    sys.stdout.write("]\n")
    sys.stdout.flush()
