#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from rscraping.clients import Client, TabularClientConfig, TabularDataClient
from rscraping.data.functions import save_csv, sys_print_items
from rscraping.data.models import Datasource

logger = logging.getLogger(__name__)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet_id_or_file_path", type=str, help="Google sheet ID or local file path.")
    parser.add_argument("race_id", type=str, nargs="?", help="Race to find.")
    parser.add_argument(
        "--female", action="store_true", default=False, help="Specifies if we need to search in the female pages."
    )
    parser.add_argument("--sheet_name", type=str, default=None, help="Sheet name.")
    parser.add_argument("--save", action="store_true", default=False, help="Saves the output to a csv file.")
    return parser.parse_args()


def main(
    sheet_id_or_file_path: str,
    is_female: bool,
    race_id: str | None = None,
    sheet_name: str | None = None,
    save: bool = False,
):
    sheet_id = sheet_id_or_file_path if not os.path.isfile(sheet_id_or_file_path) else None
    file_path = sheet_id_or_file_path if os.path.isfile(sheet_id_or_file_path) else None

    config = TabularClientConfig(file_path=file_path, sheet_id=sheet_id, sheet_name=sheet_name)
    client: TabularDataClient = Client(source=Datasource.TABULAR, config=config)  # type: ignore

    if race_id:
        race = client.get_race_by_id(race_id, is_female=is_female)
        if not race:
            raise ValueError(f"not found race for race_id={race_id}")

        if save:
            save_csv([race], file_name=f"race_{race_id}_{Datasource.TABULAR.value.upper()}")

        sys_print_items([race])
        sys.exit(0)

    races = list(client.get_races(is_female=is_female))

    if save:
        save_csv(races, file_name=f"race_{race_id}_{Datasource.TABULAR.value.upper()}")

    sys_print_items(races)


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(args.sheet_id_or_file_path, args.female, args.race_id, args.sheet_name, args.save)
