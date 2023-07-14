#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from typing import List, Optional

from data.models import Datasource, Lineup
from clients import Client
from data.functions import save_csv

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def find_lineup(race_id: str, club_id: Optional[str], datasource: Datasource, is_female: bool) -> List[Lineup]:
    if datasource == Datasource.ARC and not club_id:
        raise ValueError(f"invalid 'club_id' for {datasource=}")
    client = Client(source=datasource)  # type: ignore
    return client.get_lineup_by_race_id(race_id, club_id=club_id, is_female=is_female)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("datasource", type=str, help="Datasource from where to retrieve.")
    parser.add_argument("race_id", type=str, help="Race to find.")
    parser.add_argument("--club_id", type=str, default=None)
    parser.add_argument("--female", action="store_true", default=False)
    return parser.parse_args()


def main(race_id: str, club_id: Optional[str], datasource: str, is_female: bool):
    if datasource.upper() not in Datasource.values():
        raise ValueError(f"invalid datasource={datasource}")

    lineups = find_lineup(
        race_id=race_id,
        club_id=club_id,
        datasource=Datasource[datasource.upper()],
        is_female=is_female,
    )
    if not lineups:
        raise ValueError(f"not found lineup for race_id={args.race_id}")

    print(",\n".join(l.to_json() for l in lineups))
    save_csv(lineups, file_name=datasource.upper())


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(args.race_id, args.club_id, args.datasource, args.female)
