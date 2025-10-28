import os
import unittest
from datetime import datetime

from parsel.selector import Selector

from rscraping.data.constants import CATEGORY_ABSOLUT, GENDER_MALE, RACE_CONVENTIONAL, RACE_TRAINERA
from rscraping.data.models import Datasource, Participant, Race, RaceName
from rscraping.parsers.html.act import ACTHtmlParser


class TestACTParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = ACTHtmlParser()
        self.fixtures = os.path.join(os.getcwd(), "tests", "fixtures", "html")

    def test_parse_race(self) -> None:
        with open(os.path.join(self.fixtures, "act_details.html")) as file:
            race = self.parser.parse_race(
                Selector(file.read()),
                race_id="1234",
                is_female=False,
            )
        if not race:
            raise ValueError("unable to parse race")

        participants = race.participants
        race.participants = []

        self.assertEqual(race, self._RACE)
        self.assertEqual(participants, self._PARTICIPANTS)

    def test_parse_race_ids(self) -> None:
        with open(os.path.join(self.fixtures, "act_races.html")) as file:
            ids = self.parser.parse_race_ids(Selector(file.read()))

        self.assertEqual(list(ids), ["1616789082", "1616789390", "1616789420"])

    def test_parse_race_ids_by_days(self) -> None:
        with open(os.path.join(self.fixtures, "act_races.html")) as file:
            ids = self.parser.parse_race_ids_by_days(
                Selector(file.read()),
                days=[datetime.strptime("03-07-2021", "%d-%m-%Y")],
            )

        self.assertEqual(list(ids), ["1616789082"])

    def test_parse_race_names(self) -> None:
        with open(os.path.join(self.fixtures, "act_races.html")) as file:
            race_names = self.parser.parse_race_names(Selector(file.read()), is_female=False)

        self.assertEqual(list(race_names), self._RACE_NAMES)

    _RACE = Race(
        name="ORIOKO XXXIII. ESTROPADA - ORIO KANPINA XI. BANDERA (16-07-2023)",
        date="16/07/2023",
        day=1,
        modality=RACE_TRAINERA,
        type=RACE_CONVENTIONAL,
        league="EUSKO LABEL LIGA",
        town="ZIERBENA",
        organizer=None,
        sponsor=None,
        normalized_names=[("ORIOKO ESTROPADAK", 33), ("ORIO KANPINA BANDERA", 11)],
        race_ids=["1234"],
        url=None,
        datasource=Datasource.ACT.value,
        gender=GENDER_MALE,
        category=CATEGORY_ABSOLUT,
        participants=[],
        race_laps=4,
        race_lanes=4,
        cancelled=False,
    )
    _PARTICIPANTS = [
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="GETARIA",
            lane=3,
            series=1,
            laps=["05:03.000000", "09:57.000000", "15:20.000000", "20:09.900000"],
            distance=5556,
            handicap=None,
            participant="GETARIA",
            race=_RACE,
            absent=False,
            retired=False,
            guest=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="ZIERBENA BAHIAS DE BIZKAIA",
            lane=4,
            series=2,
            laps=["05:05.000000", "09:59.000000", "15:26.000000", "20:20.980000"],
            distance=5556,
            handicap=None,
            participant="ZIERBENA",
            race=_RACE,
            absent=False,
            retired=False,
            guest=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="MATRIX HONDARRIBIA",
            lane=2,
            series=3,
            laps=["04:57.000000", "09:44.000000", "15:05.000000", "19:54.520000"],
            distance=5556,
            handicap=None,
            participant="HONDARRIBIA",
            race=_RACE,
            absent=False,
            retired=False,
            guest=False,
        ),
    ]
    _RACE_NAMES = [
        RaceName(
            race_id="1616789082",
            name="V BANDEIRA CIDADE DA CORUÑA (J1)",
        ),
        RaceName(
            race_id="1616789390",
            name="ORIOKO XXXIII. ESTROPADA - ORIO KANPINA XI. BANDERA",
        ),
        RaceName(
            race_id="1616789420",
            name="XIII. BANDERA DONOSTIARRA - TURISMO CASTILLA-LA MANCHA",
        ),
    ]
