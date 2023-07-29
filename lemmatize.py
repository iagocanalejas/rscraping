import argparse
import logging
import os
import sys

from rscraping import lemmatize


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("phrase", type=str, help="Phrase to lemmatize.")
    return parser.parse_args()


def main(phrase: str):
    print(lemmatize(phrase))


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(args.phrase)
