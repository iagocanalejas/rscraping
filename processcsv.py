#!/usr/bin/env python3

import argparse
import logging
import os

from rscraping import find_csv_race, parse_race_csv
from rscraping.data.functions import save_csv
from rscraping.data.models import Datasource

logger = logging.getLogger(__name__)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet_id", type=str, help="Google sheet ID or local file path.")
    parser.add_argument("race_id", type=str, nargs="?", help="Race to find.")
    parser.add_argument(
        "--female",
        action="store_true",
        default=False,
        help="Specifies if we need to search in the female pages.",
    )
    parser.add_argument("--sheet_name", type=str, default=None, help="Sheet name.")
    parser.add_argument("--save", action="store_true", default=False, help="Saves the output to a csv file.")
    return parser.parse_args()


def main(sheet_id: str, is_female: bool, race_id: str | None = None, sheet_name: str | None = None, save: bool = False):
    if race_id:
        race = find_csv_race(race_id, sheet_id, is_female=is_female, sheet_name=sheet_name)
        if not race:
            raise ValueError(f"not found race for race_id={race_id}")

        print(race.to_json())
        if save:
            save_csv([race], file_name=f"race_{race_id}_{Datasource.GDRIVE.value.upper()}")
        return

    races = parse_race_csv(sheet_id, is_female=is_female, sheet_name=sheet_name)
    for r in races:
        print(r.to_json())
    if save:
        save_csv(list(races), file_name=f"race_{race_id}_{Datasource.GDRIVE.value.upper()}")


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(args.sheet_id, args.female, args.race_id, args.sheet_name, args.save)
