#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from typing import List
from pypdf import PdfReader
from parsers.pdf.lineup import LineupPdfParser
from data.functions import expand_path, save_csv
from data.models import Datasource, Lineup

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

_DEBUG = False


def main(paths: List[str], datasource: Datasource):
    parser: LineupPdfParser = LineupPdfParser(source=datasource)  # type: ignore
    parsed_items: List[Lineup] = []

    for file in paths:
        with open(file, "rb") as pdf:
            reader = PdfReader(pdf)
            for page in reader.pages:
                items = parser.parse_page(page=page)
                if items:
                    parsed_items.append(items)

    if _DEBUG:
        for item in parsed_items:
            print(f"{item.race}:: {item.club}")
            print(f"Adestrador: {item.coach}")
            print(f"Delegado: {item.delegate}")
            print(f"Patrón: {item.coxswain}")
            print(f"Estribor: {item.starboard}")
            print(f"Babor: {item.larboard}")
            print(f"Proa: {item.bow}")
            print(f"Suplentes: {item.substitute}\n")

    save_csv(parsed_items, file_name=parser.DATASOURCE.value)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to be handled")
    parser.add_argument("--datasource", type=str)
    parser.add_argument("--debug", action="store_true", default=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    _DEBUG = args.debug
    if args.datasource.upper() not in Datasource.values():
        raise ValueError(f"invalid datasource={args.datasource}")
    if args.datasource.lower() == Datasource.ARC:
        raise NotImplementedError(f"no valid implementation for datasource={Datasource.ARC}")

    main(
        paths=expand_path(os.path.abspath(args.path), valid_files=[".PDF"]),
        datasource=Datasource[args.datasource.upper()],
    )
