#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from datetime import datetime
from builder import (
    PdfItem,
    fill_fegar_form,
    fill_image_form,
    fill_national_form,
    fill_xogade_form,
    prompt_entity_data,
    prompt_extra_data,
    prompt_parent_data,
    prompt_rower_data,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def _fill_data(data: PdfItem, debug: bool) -> PdfItem:
    if debug:
        data.name = "name"
        data.surname = "surname"
        data.nif = "11753905P"
        data.gender = "HOMBRE"
        data.birth = "23/11/2000"
        data.address = "address"
        data.address_number = "15"
        data.postal_code = "15940"
        data.town = "A POBRA DO CARAMIÑAL"
        data.state = "A CORUÑA"
        data.category = "CATEGORIA"

        data.parent_name = "parent_name"
        data.parent_surname = "parent_surname"
        data.parent_dni = "11753905P"
        return data

    data = prompt_rower_data(data)
    if args.parent:
        data = prompt_parent_data(data)
    if not args.entity:
        data = prompt_entity_data(data)
    if not args.preset:
        data = prompt_extra_data(data)
    return data


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-on", type=str, help="Date signed (DD/MM/YYYY", default=datetime.now().strftime("%d/%m/%Y"))
    parser.add_argument("-t", "--type", nargs="*", help="List of files to generate", default=["all"])
    parser.add_argument(
        "-p", "--parent", action="store_true", help="Whether to ask for parental data. (False)", default=False
    )
    parser.add_argument(
        "-i",
        "--images",
        type=str,
        action="store",
        help="Folder containing the images for fegar generator.",
        default=None,
    )
    parser.add_argument(
        "--preset", action=argparse.BooleanOptionalAction, help="Whether to use the preset data. (True)", default=True
    )
    parser.add_argument(
        "--entity", action=argparse.BooleanOptionalAction, help="Whether to ask for entity data. (True)", default=True
    )
    parser.add_argument(
        "--coach", action="store_true", help="Whether the licence should be for a coach. (False)", default=False
    )
    parser.add_argument(
        "--directive", action="store_true", help="Whether the licence should be for a directive. (False)", default=False
    )
    parser.add_argument("--debug", action="store_true", default=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_arguments()
    logging.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    values: PdfItem = PdfItem.preset() if args.preset or args.debug else PdfItem()
    values = _fill_data(values, debug=args.debug)
    values.sign_on(args.on)

    if args.coach:
        values.is_coach = True
    elif args.directive:
        values.is_directive = True
    else:
        values.is_rower = True

    if "national" in args.type or "all" in args.type:
        fill_national_form(values, with_parent=args.parent)
    if "image" in args.type or "all" in args.type:
        fill_image_form(values, with_parent=args.parent)
    if "fegar" in args.type or "all" in args.type:
        fill_fegar_form(values, images_folder=args.images, with_parent=args.parent, remove_temp_files=not args.debug)
    if args.parent and ("xogade" in args.type or "all" in args.type):
        fill_xogade_form(values)
