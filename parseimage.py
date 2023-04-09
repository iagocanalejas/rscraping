import argparse
import logging
import os
import sys
from typing import List

from src.ocr import ImageOCR
from src.utils.functions import expand_path, save_csv
from src.utils.models import OCR, RaceItem

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

_DEBUG = False


def main(paths: List[str], datasource: str):
    parsed_items: List[RaceItem] = []
    scrapper: ImageOCR = ImageOCR(source=datasource, allow_plot=_DEBUG)
    scrapper.set_language('es_ES.utf8')

    for file in paths:
        parsed_items.extend(scrapper.digest(path=file))

    save_csv(parsed_items, file_name=scrapper.DATASOURCE)


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
    if args.datasource.upper() not in OCR.values():
        raise ValueError(f"invalid datasource={args.datasource}")

    main(
        paths=expand_path(os.path.abspath(args.path), valid_files=['.JPG', '.JPEG', '.PNG']),
        datasource=args.datasource.lower(),
    )
