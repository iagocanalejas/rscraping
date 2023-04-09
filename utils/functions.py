import csv
import os
from typing import List

from utils.models import LineUpItem


def expand_path(path: str, valid_files: List[str]) -> List[str]:
    def is_valid(file: str) -> bool:
        _, extension = os.path.splitext(file)
        return extension.upper() in valid_files

    files = [os.path.join(path, file) for file in os.listdir(path)] if os.path.isdir(path) else [path]
    return [f for f in files if is_valid(f)]


def save_csv(items: List[LineUpItem], file_name: str):
    if not len(items):
        return

    file_name = file_name if '.csv' in file_name else f'{file_name}.csv'
    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(items[0].__dict__.keys())  # write headers
        for item in items:
            writer.writerow(item.__dict__.values())
