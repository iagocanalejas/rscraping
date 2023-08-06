import logging
import re
from ._parser import HtmlParser
from typing import List, Optional
from parsel import Selector
from pyutils.strings import find_date, whitespaces_clean
from rscraping.data.constants import (
    GENDER_MALE,
    PARTICIPANT_CATEGORY_ABSOLUT,
    RACE_CONVENTIONAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Datasource, Participant, Race, RaceName
from rscraping.data.normalization.clubs import normalize_club_name
from rscraping.data.normalization.times import normalize_lap_time
from rscraping.data.normalization.races import find_race_sponsor, normalize_name_parts, normalize_race_name

logger = logging.getLogger(__name__)


class ABEHtmlParser(HtmlParser):
    DATASOURCE = Datasource.ABE

    def parse_race(self, selector: Selector, race_id: str, **_) -> Optional[Race]:
        name = self.get_name(selector)
        if not name:
            logger.error(f"{self.DATASOURCE}: no race found for {race_id=}")
            return None
        logger.info(f"{self.DATASOURCE}: found race {name}")

        t_date = find_date(name)

        if not t_date:
            raise ValueError(f"{self.DATASOURCE}: no date found for {name=}")

        normalized_names = normalize_name_parts(normalize_race_name(name))
        if len(normalized_names) == 0:
            logger.error(f"{self.DATASOURCE}: unable to normalize {name=}")
            return None
        logger.info(f"{self.DATASOURCE}: race normalized to {normalized_names=}")

        participants = self.get_participants(selector)

        race = Race(
            name=self.get_name(selector),
            normalized_names=normalized_names,
            date=t_date.strftime("%d/%m/%Y"),
            type=RACE_CONVENTIONAL,
            day=self.get_day(selector),
            modality=RACE_TRAINERA,
            league="ARRAUNLARI BETERANOEN ELKARTEA",
            town=None,
            organizer=None,
            sponsor=find_race_sponsor(self.get_name(selector)),
            race_id=race_id,
            url=None,
            gender=GENDER_MALE,
            datasource=self.DATASOURCE.value,
            cancelled=False,
            race_laps=None,
            race_lanes=None,
            participants=[],
        )

        for row in participants:
            race.participants.append(
                Participant(
                    gender=GENDER_MALE,
                    category=PARTICIPANT_CATEGORY_ABSOLUT,
                    club_name=self.get_club_name(row),
                    lane=None,
                    series=None,
                    laps=self.get_laps(row),
                    distance=2778,
                    handicap=self.get_handicap(row),
                    participant=normalize_club_name(self.get_club_name(row)),
                    race=race,
                    disqualified=False,
                )
            )

        return race

    def parse_race_ids(self, selector: Selector, **_) -> List[str]:
        urls = selector.xpath(
            '//*[@id="page"]/div/section[2]/div[2]/div[1]/div/div[2]/div/div/article[*]/div/h3/a/@href'
        ).getall()
        return [url_parts[-2] for url_parts in (url.split("/") for url in urls)]

    def parse_race_names(self, selector: Selector, **_) -> List[RaceName]:
        hrefs = selector.xpath(
            '//*[@id="page"]/div/section[2]/div[2]/div[1]/div/div[2]/div/div/article[*]/div/h3/a'
        ).getall()
        selectors = [Selector(h) for h in hrefs]
        pairs = [(s.xpath("//*/@href").get("").split("/")[-2], s.xpath("//*/text()").get("")) for s in selectors]
        return [RaceName(p[0], whitespaces_clean(p[1]).upper()) for p in pairs]

    def parse_lineup(self, **_):
        raise NotImplementedError

    ####################################################
    #                     GETTERS                      #
    ####################################################

    def get_name(self, selector: Selector) -> str:
        return whitespaces_clean(
            selector.xpath('//*[@id="page"]/div/section/div/div/div/div/div/h1/text()').get("")
        ).upper()

    def get_day(self, selector: Selector) -> int:
        name = self.get_name(selector)
        matches = re.findall(r"\(?(\dJ|J\d)\)?", name)
        return int(re.findall(r"\d+", matches[0])[0].strip()) if matches else 1

    def get_participants(self, selector: Selector) -> List[Selector]:
        rows = selector.xpath('//*[@id="page"]/div/section/div/div/div/div/div/table/tbody/tr[*]').getall()
        return [Selector(text=t) for t in rows[1:]]

    def get_club_name(self, participant: Selector) -> str:
        name = participant.xpath("//*/td[2]/text()").get()
        return whitespaces_clean(name).upper() if name else ""

    def get_laps(self, participant: Selector) -> List[str]:
        lap = normalize_lap_time(participant.xpath("//*/td[3]/text()").get(""))
        return [lap.strftime("%M:%S.%f")] if lap is not None else []

    def get_handicap(self, participant: Selector) -> Optional[str]:
        if len(participant.xpath("//*/td[*]/text()").getall()) <= 4:
            return None
        lap = normalize_lap_time(participant.xpath("//*/td[4]/text()").get(""))
        return lap.strftime("%M:%S.%f") if lap else None
