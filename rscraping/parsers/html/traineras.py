import logging
from ._parser import HtmlParser
from typing import List, Optional
from parsel import Selector
from pyutils.strings import find_date, whitespaces_clean
from rscraping.data.constants import (
    GENDER_FEMALE,
    GENDER_MALE,
    PARTICIPANT_CATEGORY_ABSOLUT,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Datasource, Participant, Race
from rscraping.data.normalization.clubs import normalize_club_name
from rscraping.data.normalization.times import normalize_lap_time
from rscraping.data.normalization.races import normalize_race_name

logger = logging.getLogger(__name__)


class MultiDayRaceException(Exception):
    pass


class TrainerasHtmlParser(HtmlParser):
    """
    - both race 'day' are saved in the same 'ref_id'
    - 'edition' can't be retrieved
    - 'league' can't be retrieved
    """

    DATASOURCE = Datasource.TRAINERAS

    _FEMALE = ["SF", "VF", "JF"]

    def parse_race(self, selector: Selector, race_id: str, day: Optional[int] = None, **_) -> Optional[Race]:
        if len(selector.xpath("/html/body/div[1]/main/div[1]/div/div/div[2]/table[*]").getall()) > 1 and not day:
            raise MultiDayRaceException()
        day = day if day else 1

        name = self.get_name(selector)
        logger.info(f"{self.DATASOURCE}: found race {name}")

        t_date = find_date(selector.xpath("/html/body/div[1]/main/div/div/div/div[1]/h2/text()").get(""))
        gender = self.get_gender(selector)
        distance = self.get_distance(selector)

        if not t_date:
            raise ValueError(f"{self.DATASOURCE}: no date found for {name=}")

        if not name:
            logger.error(f"{self.DATASOURCE}: no race found for {race_id=}")
            return None
        logger.info(f"{self.DATASOURCE}: race normalized to {name=}")

        participants = self.get_participants(selector, day)
        ttype = self.get_type(participants)

        race = Race(
            name=name,
            normalized_name=normalize_race_name(name, False),
            date=t_date.strftime("%d/%m/%Y"),
            type=ttype,
            edition=1,  # not present
            day=day,
            modality=RACE_TRAINERA,
            league=None,  # not present
            town=self.get_town(selector),
            organizer=None,
            race_id=race_id,
            url=None,
            gender=gender,
            datasource=self.DATASOURCE.value,
            cancelled=self.is_cancelled(),
            race_laps=self.get_race_laps(selector, day),
            race_lanes=self.get_race_lanes(participants),
            participants=[],
        )

        for row in participants:
            race.participants.append(
                Participant(
                    gender=gender,
                    category=PARTICIPANT_CATEGORY_ABSOLUT,
                    club_name=self.get_club_name(row),
                    lane=self.get_lane(row) if ttype == RACE_CONVENTIONAL else 1,
                    series=self.get_series(selector) if ttype == RACE_CONVENTIONAL else 1,
                    laps=self.get_laps(row),
                    distance=distance,
                    participant=normalize_club_name(self.get_club_name(row)),
                    race=race,
                )
            )

        return race

    def parse_race_ids(self, selector: Selector, **_) -> List[str]:
        ids = selector.xpath("/html/body/div[1]/div[2]/table/tbody/tr/td[1]/a/@href").getall()
        return [e.split("/")[-1] for e in ids]

    def parse_lineup(self, **_):
        raise NotImplementedError

    def get_number_of_pages(self, selector: Selector) -> int:
        return len(selector.xpath("/html/body/div[1]/div[3]/nav/ul/li[*]").getall()) - 2

    ####################################################
    #                     GETTERS                      #
    ####################################################

    def get_name(self, selector: Selector) -> str:
        name = whitespaces_clean(selector.xpath("/html/body/div[1]/div/h1/text()").get("")).upper()
        name = " ".join(name.split()[:-1])
        return name

    def get_gender(self, selector: Selector) -> str:
        parts = selector.xpath("/html/body/div[1]/main/div/div/div/div[1]/h2/text()").get("")
        part = whitespaces_clean(parts.split(" - ")[-1])
        return GENDER_FEMALE if part in self._FEMALE else GENDER_MALE

    def get_type(self, participants: List[Selector]) -> str:
        series = [p.xpath("//*/td[4]/text()").get("") for p in participants]
        return RACE_TIME_TRIAL if len(set(series)) == len(series) else RACE_CONVENTIONAL

    def get_town(self, selector: Selector) -> str:
        parts = selector.xpath("/html/body/div[1]/main/div/div/div/div[1]/h2/text()").get("")
        return whitespaces_clean(parts.split(" - ")[0]).upper()

    def get_race_lanes(self, participants: List[Selector]) -> int:
        if self.get_type(participants) == RACE_TIME_TRIAL:
            return 1
        lanes = list(self.get_lane(p) for p in participants)
        return max(int(lane) for lane in lanes)

    def get_race_laps(self, selector: Selector, day: int) -> int:
        cia = selector.xpath(f"/html/body/div[1]/main/div[1]/div/div/div[2]/table[{day}]/tr[1]/th/text()").getall()
        return len(cia) - 6

    def is_cancelled(self) -> bool:
        # TODO: find a cancelled race
        return False

    def get_participants(self, selector: Selector, day: int) -> List[Selector]:
        rows = selector.xpath(f"/html/body/div[1]/main/div[1]/div/div/div[2]/table[{day}]/tr").getall()
        return [Selector(text=t) for t in rows][1:]

    def get_lane(self, participant: Selector) -> int:
        lane = participant.xpath("//*/td[3]/text()").get()
        return int(lane) if lane else 0

    def get_club_name(self, participant: Selector) -> str:
        name = participant.xpath("//*/td[2]/text()").get()
        return whitespaces_clean(name).upper() if name else ""

    def get_distance(self, selector: Selector) -> int:
        parts = whitespaces_clean(selector.xpath("/html/body/div[1]/main/div/div/div/div[1]/h2/text()").get(""))
        part = parts.split(" - ")[-2]
        return part is not None and int(part.replace(" metros", ""))

    def get_laps(self, participant: Selector) -> List[str]:
        laps = participant.xpath("//*/td/text()").getall()[2:-4]
        return [t.strftime("%M:%S.%f") for t in [normalize_lap_time(e) for e in laps if e] if t is not None]

    def get_series(self, participant: Selector) -> int:
        lane = participant.xpath("//*/td[4]/text()").get()
        return int(lane) if lane else 0
