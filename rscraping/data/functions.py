import csv
import os
import sys
from typing import Any

import cv2

from rscraping.data.models import Race


def expand_path(path: str, valid_files: list[str]) -> list[str]:
    def is_valid(file: str) -> bool:
        _, extension = os.path.splitext(file)
        return extension.upper() in valid_files

    files = [os.path.join(path, file) for file in os.listdir(path)] if os.path.isdir(path) else [path]
    return [f for f in files if is_valid(f)]


def save_csv(items: list[Race], file_name: str):
    if not len(items):
        return

    file_name = file_name if ".csv" in file_name else f"{file_name}.csv"
    with open(file_name, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(items[0].__dict__.keys())  # write headers
        for item in items:
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


def draw_bounding_boxes(image, detections, threshold=0.25):
    for bbox, text, score in detections:
        if score > threshold:
            cv2.rectangle(image, tuple(map(int, bbox[0])), tuple(map(int, bbox[2])), (0, 255, 0), 5)
            cv2.putText(image, text, tuple(map(int, bbox[0])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.65, (255, 0, 0), 2)
