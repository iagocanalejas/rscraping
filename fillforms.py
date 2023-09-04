#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from datetime import datetime
from typing import List

from rscraping.builder import (
    PdfItem,
    fill_fegar_form,
    fill_image_form,
    fill_national_form,
    fill_xogade_form,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def main(
    signed_on: str,
    types: List[str],
    image_path: str,
    use_preset: bool,
    prompt_entity: bool,
    is_coach: bool,
    is_directive: bool,
    has_parent: bool,
    debug: bool,
):
    data = PdfItem.preset() if use_preset else PdfItem()
    data.sign_on(signed_on)

    data.is_coach = is_coach
    data.is_directive = is_directive
    data.is_rower = not is_coach and not is_directive

    data.prompt_data(prompt_entity=prompt_entity, has_parent=has_parent, use_preset=use_preset, debug=debug)

    if "national" in types or "all" in types:
        fill_national_form(data, with_parent=has_parent)
    if "image" in types or "all" in types:
        fill_image_form(data, with_parent=args.parent)
    if "fegar" in types or "all" in types:
        fill_fegar_form(data, images_folder=image_path, with_parent=has_parent, remove_temp_files=not debug)
    if has_parent and ("xogade" in types or "all" in types):
        fill_xogade_form(data)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-on", type=str, help="Date signed (DD/MM/YYYY", default=datetime.now().strftime("%d/%m/%Y"))
    parser.add_argument("-t", "--type", nargs="*", help="List of files to generate", default=["all"])
    parser.add_argument(
        "-p",
        "--parent",
        action="store_true",
        help="Whether to ask for parental data. (False)",
        default=False,
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
        "--preset",
        action=argparse.BooleanOptionalAction,
        help="Whether to use the preset data. (True)",
        default=True,
    )
    parser.add_argument(
        "--entity",
        action=argparse.BooleanOptionalAction,
        help="Whether to ask for entity data. (True)",
        default=True,
    )
    parser.add_argument(
        "--coach",
        action="store_true",
        help="Whether the licence should be for a coach. (False)",
        default=False,
    )
    parser.add_argument(
        "--directive",
        action="store_true",
        help="Whether the licence should be for a directive. (False)",
        default=False,
    )
    parser.add_argument("--debug", action="store_true", default=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_arguments()
    logging.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    signed_on, types, image_path, use_preset, prompt_entity, is_coach, is_directive, has_parent, debug = (
        args.on,
        args.type,
        args.images,
        args.preset or args.debug,
        args.entity,
        args.coach,
        args.directive,
        args.parent,
        args.debug,
    )

    if image_path:
        assert os.path.isdir(image_path)

    main(signed_on, types, image_path, use_preset, prompt_entity, is_coach, is_directive, has_parent, debug)
