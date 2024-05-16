#!/usr/bin/env python3

import argparse
import logging
import os
import sys

sys.path[0] = os.path.join(os.path.dirname(__file__), "..")
logger = logging.getLogger(__name__)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("phrase", type=str, help="Phrase to lemmatize.")
    return parser.parse_args()


def main(phrase: str):
    sys_print_items(lemmatize(phrase))


if __name__ == "__main__":
    from rscraping import lemmatize
    from rscraping.data.functions import sys_print_items

    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(args.phrase)
