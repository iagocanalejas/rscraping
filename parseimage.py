#!/usr/bin/env python3

import argparse
import logging
import os

from rscraping import parse_race_image
from rscraping.data.functions import expand_path, save_csv
from rscraping.data.models import Datasource, Race

logger = logging.getLogger(__name__)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("datasource", type=str, help="Datasource from where to retrieve.")
    parser.add_argument("path", help="Path to be handled")
    parser.add_argument("--header", type=int, help="Amount of the image representing the header (1/split)")
    parser.add_argument("--save", action="store_true", default=False, help="Saves the output to a csv file.")
    parser.add_argument("--debug", action="store_true", default=False, help="Plot the images to see the processing.")
    return parser.parse_args()


def main(paths: list[str], datasource: str, header_size: int = 3, allow_plot: bool = False, save: bool = False):
    if not Datasource.is_OCR(datasource):
        raise ValueError(f"invalid datasource={datasource}")

    parsed_items: list[Race] = []
    for path in paths:
        parsed_items.extend(
            parse_race_image(
                path,
                datasource=Datasource(datasource),
                header_size=header_size,
                allow_plot=allow_plot,
            )
        )

    for race in parsed_items:
        print(race.to_json())

    if save:
        save_csv(parsed_items, file_name=f"img_races_{datasource.upper()}")


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(
        paths=expand_path(os.path.abspath(args.path), valid_files=[".JPG", ".JPEG", ".PNG"]),
        datasource=args.datasource,
        header_size=args.header or 3,
        allow_plot=args.debug,
        save=args.save,
    )
