#!/usr/bin/env python3

import argparse
import logging
import os

from rscraping import find_race
from rscraping.data.functions import save_csv
from rscraping.data.models import Datasource

logger = logging.getLogger(__name__)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("datasource", type=str, help="Datasource from where to retrieve.")
    parser.add_argument("race_id", type=str, help="Race to find.")
    parser.add_argument(
        "--female",
        action="store_true",
        default=False,
        help="Specifies if we need to search in the female pages.",
    )
    parser.add_argument("--day", type=int, help="Day we want (for multi races pages).")
    parser.add_argument("--lineups", action="store_true", default=False, help="Tryies to fill the lineups.")
    parser.add_argument("--save", action="store_true", default=False, help="Saves the output to a csv file.")
    return parser.parse_args()


def main(race_id: str, datasource: str, is_female: bool, with_lineups: bool, save: bool, day: int | None):
    if not Datasource.has_value(datasource):
        raise ValueError(f"invalid datasource={datasource}")

    race = find_race(
        race_id=race_id,
        datasource=Datasource(datasource),
        is_female=is_female,
        with_lineup=with_lineups,
        day=day,
    )
    if not race:
        raise ValueError(f"not found race for race_id={race_id}")

    print(race.to_json())
    if save:
        save_csv([race], file_name=f"race_{race_id}_{datasource.upper()}")


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(args.race_id, args.datasource, args.female, args.lineups, args.save, args.day)
