import argparse
import logging
import os
import sys

from src.url.lineup import LineupUrlParser
from src.utils.functions import save_csv
from src.utils.models import Datasource

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

_DEBUG = False


def main(url: str, datasource: str):
    parser: LineupUrlParser = LineupUrlParser(source=datasource)
    parsed_item = parser.parse_page(url)

    if _DEBUG:
        print(f"{parsed_item.race}:: {parsed_item.club}")
        print(f"Adestrador: {parsed_item.coach}")
        print(f"Delegado: {parsed_item.delegate}")
        print(f"Patrón: {parsed_item.coxswain}")
        print(f"Estribor: {parsed_item.starboard}")
        print(f"Babor: {parsed_item.larboard}")
        print(f"Proa: {parsed_item.bow}")
        print(f"Suplentes: {parsed_item.substitute}\n")

    save_csv([parsed_item], file_name=parser.DATASOURCE)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Url to be handled')
    parser.add_argument('--datasource', type=str)
    parser.add_argument('--debug', action='store_true', default=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_arguments()
    logger.info(f'{os.path.basename(__file__)}:: args -> {args.__dict__}')

    _DEBUG = args.debug
    if args.datasource.upper() not in Datasource.values():
        raise ValueError(f"invalid datasource={args.datasource}")
    if args.datasource.lower() != Datasource.ARC:
        raise NotImplementedError(f"no valid implementation for datasource={args.datasource.upper()}")

    main(
        url=args.url,
        datasource=args.datasource.lower(),
    )
