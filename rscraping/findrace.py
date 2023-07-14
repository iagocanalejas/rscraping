#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from typing import Optional

from data.models import Datasource, Race
from clients import Client

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def find_race(race_id: str, datasource: Datasource, is_female: bool) -> Optional[Race]:
    client = Client(source=datasource)  # type: ignore
    return client.get_race_by_id(race_id, is_female=is_female)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("datasource", type=str, help="Datasource from where to retrieve.")
    parser.add_argument("race_id", type=str, help="Race to find.")
    parser.add_argument("--female", action="store_true", default=False)
    return parser.parse_args()


def main(race_id: str, datasource: str, is_female: bool):
    if datasource.upper() not in Datasource.values():
        raise ValueError(f"invalid datasource={datasource}")

    race = find_race(
        race_id=race_id,
        datasource=Datasource[datasource.upper()],
        is_female=is_female,
    )
    if not race:
        raise ValueError(f"not found race for race_id={args.race_id}")

    print(race.to_json())


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(args.race_id, args.datasource, args.female)
