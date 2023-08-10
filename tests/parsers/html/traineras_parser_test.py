import os
import unittest

from parsel import Selector

from rscraping.data.constants import GENDER_MALE
from rscraping.data.models import Participant, Race, RaceName
from rscraping.parsers.html.traineras import MultiDayRaceException, TrainerasHtmlParser


class TestTrainerasParser(unittest.TestCase):
    def setUp(self):
        self.parser = TrainerasHtmlParser()
        self.fixtures = os.path.join(os.getcwd(), "fixtures", "html")

    def test_multi_day_race_exception(self):
        with open(os.path.join(self.fixtures, "traineras_details.html")) as file:
            with self.assertRaises(MultiDayRaceException):
                self.parser.parse_race(
                    Selector(file.read()),
                    race_id="1234",
                )

    def test_parse_race(self):
        with open(os.path.join(self.fixtures, "traineras_details.html")) as file:
            selector = Selector(file.read())
            race_1 = self.parser.parse_race(
                selector,
                race_id="1234",
                day=1,
            )
            race_2 = self.parser.parse_race(
                selector,
                race_id="1234",
                day=2,
            )
        if not race_1 or not race_2:
            raise ValueError("unable to parse race")

        participants = race_1.participants
        race_1.participants = []

        self.assertEqual(race_1, self._RACE_1)
        self.assertEqual(participants, self._PARTICIPANTS)

    def test_parse_race_ids(self):
        with open(os.path.join(self.fixtures, "traineras_results.html")) as file:
            ids = self.parser.parse_race_ids(Selector(file.read()))

        self.assertEqual(ids, ["5455", "5456", "5457", "5458", "5535", "5536"])

    def test_parse_race_names(self):
        with open(os.path.join(self.fixtures, "traineras_results.html")) as file:
            race_names = self.parser.parse_race_names(Selector(file.read()))

        self.assertEqual(race_names, self._RACE_NAMES)

    def test_get_number_of_pages(self):
        with open(os.path.join(self.fixtures, "traineras_results.html")) as file:
            self.assertEqual(self.parser.get_number_of_pages(Selector(file.read())), 1)

    _RACE_1 = Race(
        name="BANDERA CIUDAD DE LA CORUÑA",
        date="09/07/2022",
        day=1,
        modality="TRAINERA",
        type="CONVENTIONAL",
        league=None,
        town="A CORUÑA",
        organizer=None,
        sponsor=None,
        normalized_names=[("BANDERA CIUDAD DE LA CORUÑA", None)],
        race_id="1234",
        url=None,
        gender=GENDER_MALE,
        datasource="traineras",
        participants=[],
        race_laps=4,
        race_lanes=4,
        cancelled=False,
    )
    _RACE_2 = Race(
        name="BANDERA CIUDAD DE LA CORUÑA",
        date="09/07/2022",
        day=2,
        modality="TRAINERA",
        type="CONVENTIONAL",
        league=None,
        town="A CORUÑA",
        organizer=None,
        sponsor=None,
        normalized_names=[("BANDERA CIUDAD DE LA CORUÑA", None)],
        race_id="1234",
        url=None,
        gender=GENDER_MALE,
        datasource="traineras",
        participants=[],
        race_laps=4,
        race_lanes=4,
        cancelled=False,
    )
    _PARTICIPANTS = [
        Participant(
            gender="MALE",
            category="ABSOLUT",
            club_name="URDAIBAI A.E.",
            lane=1,
            series=3,
            laps=["05:08.000000", "09:59.000000", "15:30.000000", "20:17.260000"],
            distance=5556,
            handicap=None,
            participant="URDAIBAI",
            race=_RACE_1,
            disqualified=False,
        ),
        Participant(
            gender="MALE",
            category="ABSOLUT",
            club_name="C.R.O. ORIO A.E.",
            lane=4,
            series=3,
            laps=["05:09.000000", "10:06.000000", "15:38.000000", "20:24.700000"],
            distance=5556,
            handicap=None,
            participant="ORIO",
            race=_RACE_1,
            disqualified=False,
        ),
    ]
    _RACE_NAMES = [
        RaceName(race_id="5455", name="MEMORIAL PEPE O RUSO"),
        RaceName(race_id="5456", name="MEMORIAL PEPE O RUSO"),
        RaceName(race_id="5457", name="MEMORIAL PEPE O RUSO"),
        RaceName(race_id="5458", name="MEMORIAL PEPE O RUSO"),
        RaceName(race_id="5535", name="MEMORIAL AURORA TRUEBA"),
        RaceName(race_id="5536", name="MEMORIAL AURORA TRUEBA"),
    ]