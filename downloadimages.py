#!/usr/bin/env python3

import argparse
import logging
import os
import time

import requests
from parsel.selector import Selector

from pyutils.strings import find_date
from rscraping.clients import Client
from rscraping.clients.traineras import TrainerasClient
from rscraping.data.constants import HTTP_HEADERS
from rscraping.data.models import Datasource
from rscraping.parsers.html.traineras import TrainerasHtmlParser

logger = logging.getLogger(__name__)


# this only works with traineras.es
def main(rower_id: str, club_name: str, year: str | None = None, output: str = "./out"):
    client: TrainerasClient = Client(source=Datasource.TRAINERAS)  # type: ignore
    parser: TrainerasHtmlParser = client._html_parser  # type: ignore

    for race_id in client.get_race_ids_by_rower(rower_id, year=year):
        content = requests.get(url=client.get_race_details_url(race_id), headers=HTTP_HEADERS()).content.decode("utf-8")
        selector = Selector(content)

        t_date = find_date(selector.xpath(f"/html/body/div[1]/main/div/div/div/div[{1}]/h2/text()").get(""))
        t_date = t_date.strftime("%d%m%Y") if t_date else None
        participants: list[Selector] = parser.get_participants(selector, day=1)
        for participant in participants:
            if (
                club_name.upper() not in parser.get_club_name(participant)
                or participant.xpath("//*/td[10]/a/text()").get("") == "No"
            ):
                logger.error(f"no image found for {t_date}")
                continue
            retrieve_images(participant.xpath("//*/td[10]/a/@href").get(""), t_date, output)
        time.sleep(20)


def retrieve_images(url: str, t_date: str | None, output: str):
    content = requests.get(url=url, headers=HTTP_HEADERS()).content.decode("utf-8")
    selector = Selector(content)

    logger.info(f"downloading images for {t_date}")
    for id, img in enumerate(selector.xpath('//*[@id="fotografias"]/a/img/@src').getall()):
        content = requests.get(url=img, headers=HTTP_HEADERS()).content
        extension = img.split(".")[-1]
        with open(f"./{output}/{t_date}_{id}.{extension}", "wb") as file:
            file.write(content)
        time.sleep(1)


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("rower_id", type=str, help="Rower to search.")
    parser.add_argument("club", type=str, help="Club to find races.")
    parser.add_argument("--year", type=str, default=None, help="Year to download.")
    parser.add_argument("--output", type=str, default="./out", help="Output folder.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_arguments()
    logger.info(f"{os.path.basename(__file__)}:: args -> {args.__dict__}")

    main(args.rower_id, args.club, args.year, args.output)
