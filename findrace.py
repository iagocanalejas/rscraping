#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from rscraping import find_race
from rscraping.data.models import Datasource

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("datasource", type=str, help="Datasource from where to retrieve.")
    parser.add_argument("race_id", type=str, help="Race to find.")
    parser.add_argument("--female", action="store_true", default=False)
    return parser.parse_args()


def main(race_id: str, datasource: str, is_female: bool):
    if not Datasource.has_value(datasource):
        raise ValueError(f"invalid datasource={datasource}")

    race = find_race(
        race_id=race_id,
        datasource=Datasource(datasource),
        is_female=is_female,
    )
    if not race:
        raise ValueError(f"not found race for race_id={args.race_id}")

    print(race.to_json())


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(args.race_id, args.datasource, args.female)
