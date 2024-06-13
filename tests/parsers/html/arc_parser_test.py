import os
import unittest

from parsel.selector import Selector

from rscraping.data.constants import CATEGORY_ABSOLUT, GENDER_MALE, RACE_TIME_TRIAL, RACE_TRAINERA
from rscraping.data.models import Datasource, Participant, Race, RaceName
from rscraping.parsers.html.arc import ARCHtmlParser


class TestARCParser(unittest.TestCase):
    def setUp(self):
        self.parser = ARCHtmlParser()
        self.fixtures = os.path.join(os.getcwd(), "tests", "fixtures", "html")

    def test_parse_race(self):
        with open(os.path.join(self.fixtures, "arc_details.html")) as file:
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

    def test_parse_race_ids(self):
        with open(os.path.join(self.fixtures, "arc_races.html")) as file:
            ids = self.parser.parse_race_ids(Selector(file.read()))

        self.assertEqual(list(ids), ["446", "474", "475"])

    def test_parse_race_names(self):
        with open(os.path.join(self.fixtures, "arc_races.html")) as file:
            race_names = self.parser.parse_race_names(Selector(file.read()), is_female=False)

        self.assertEqual(list(race_names), self._RACE_NAMES)

    _RACE = Race(
        name="XVII BANDERA RIA DEL ASON",
        date="22/08/2009",
        day=1,
        modality=RACE_TRAINERA,
        type=RACE_TIME_TRIAL,
        league="ASOCIACIÓN DE REMO DEL CANTÁBRICO 2",
        town="COLINDRES",
        organizer=None,
        sponsor=None,
        normalized_names=[("BANDERA RIA DEL ASON", 17)],
        race_ids=["1234"],
        url=None,
        gender=GENDER_MALE,
        category=CATEGORY_ABSOLUT,
        datasource=Datasource.ARC.value,
        participants=[],
        race_laps=4,
        race_lanes=7,
        cancelled=False,
    )
    _PARTICIPANTS = [
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="RASPAS A.E.",
            lane=1,
            series=1,
            laps=["06:08.000000", "11:12.000000", "17:44.000000", "22:43.450000"],
            distance=5556,
            handicap=None,
            participant="RASPAS",
            race=_RACE,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="NATURHOUSE - MUNDAKA",
            lane=1,
            series=2,
            laps=["05:29.000000", "10:29.000000", "16:16.000000", "21:13.900000"],
            distance=5556,
            handicap=None,
            participant="MUNDAKA",
            race=_RACE,
        ),
    ]
    _RACE_NAMES = [
        RaceName(
            race_id="446",
            name="KEPA DEUN ARRANTZALEEN KOFRADIA XXII. IKURRIÑA",
        ),
        RaceName(race_id="474", name="PLAY OFF I"),
        RaceName(race_id="475", name="PLAY OFF II"),
    ]
