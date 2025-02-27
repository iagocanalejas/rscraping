#!/usr/bin/env python3
import argparse
import logging
import os
import sys

sys.path[0] = os.path.join(os.path.dirname(__file__), "..")
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
    parser.add_argument("--table", type=int, help="Table we want (for multi races pages).")
    parser.add_argument("--save", action="store_true", default=False, help="Saves the output to a csv file.")
    return parser.parse_args()


def main(race_id: str, datasource: str, is_female: bool, save: bool, table: int | None):
    if not Datasource.has_value(datasource):
        raise ValueError(f"invalid datasource={datasource}")

    race = find_race(
        race_id=race_id,
        datasource=Datasource(datasource),
        is_female=is_female,
        table=table,
    )
    if not race:
        raise ValueError(f"not found race for race_id={race_id}")

    if save:
        save_csv([race], file_name=f"race_{race_id}_{datasource.upper()}")

    sys_print_items([race])


if __name__ == "__main__":
    from rscraping import find_race
    from rscraping.data.functions import save_csv, sys_print_items
    from rscraping.data.models import Datasource

    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(args.race_id, args.datasource, args.female, args.save, args.table)
