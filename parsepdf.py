import argparse
import logging
import os
import sys
from typing import List

from PyPDF2 import PdfReader

from src.pdf.lineup import LineUpParser
from src.utils.functions import expand_path, save_csv
from src.utils.models import Datasource, LineUpItem

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

_DEBUG = False


def main(paths: List[str], datasource: str):
    parser: LineUpParser = LineUpParser(source=datasource)
    parsed_items: List[LineUpItem] = []

    for file in paths:
        with open(file, 'rb') as pdf:
            reader = PdfReader(pdf)
            for page in reader.pages:
                items = parser.parse_page(page)
                if items:
                    parsed_items.append(items)

    if _DEBUG:
        for item in parsed_items:
            print(f"{item.race}::{item.club}")
            print(f"Adestrador: {item.coach}")
            print(f"Delegado: {item.delegate}")
            print(f"Patrón: {item.coxswain}")
            print(f"Estribor: {item.starboard}")
            print(f"Babor: {item.larboard}")
            print(f"Proa: {item.bow}")
            print(f"Suplentes: {item.substitute}\n")

    save_csv(parsed_items, file_name=parser.DATASOURCE)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Path to be handled')
    parser.add_argument('--datasource', type=str)
    parser.add_argument('--debug', action='store_true', default=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_arguments()
    logger.info(f'{os.path.basename(__file__)}:: args -> {args.__dict__}')

    _DEBUG = args.debug
    if args.datasource.upper() not in Datasource.values():
        raise ValueError(f"invalid datasource={args.datasource}")

    main(
        paths=expand_path(os.path.abspath(args.path), valid_files=['.PDF']),
        datasource=args.datasource.lower(),
    )
