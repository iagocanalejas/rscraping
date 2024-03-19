import os
import unittest

from parsel.selector import Selector

from rscraping.data.constants import CATEGORY_VETERAN, GENDER_MALE, RACE_CONVENTIONAL, RACE_TRAINERA
from rscraping.data.models import Datasource, Participant, Race, RaceName
from rscraping.parsers.html import ABEHtmlParser


class TestABEParser(unittest.TestCase):
    def setUp(self):
        self.parser = ABEHtmlParser()
        self.fixtures = os.path.join(os.getcwd(), "fixtures", "html")

    def test_parse_race(self):
        with open(os.path.join(self.fixtures, "abe_details.html")) as file:
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
        with open(os.path.join(self.fixtures, "abe_races.html")) as file:
            ids = self.parser.parse_race_ids(Selector(file.read()))

        self.assertEqual(list(ids), ["getxo", "plentzia", "fortuna"])

    def test_parse_race_names(self):
        with open(os.path.join(self.fixtures, "abe_races.html")) as file:
            race_names = self.parser.parse_race_names(Selector(file.read()), is_female=False)

        self.assertEqual(list(race_names), self._RACE_NAMES)

    _RACE = Race(
        name="XIII BANDERA CRV PONTEJOS (3/6/2023)",
        date="03/06/2023",
        day=1,
        modality=RACE_TRAINERA,
        type=RACE_CONVENTIONAL,
        league="ARRAUNLARI BETERANOEN ELKARTEA",
        town=None,
        organizer=None,
        sponsor=None,
        normalized_names=[("BANDERA CRV PONTEJOS", 13)],
        race_ids=["1234"],
        url=None,
        datasource=Datasource.ABE.value,
        gender=GENDER_MALE,
        participants=[],
        race_laps=None,
        race_lanes=None,
        cancelled=False,
    )
    _PARTICIPANTS = [
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_VETERAN,
            club_name="FORTUNA",
            lane=None,
            series=None,
            laps=["14:16.010000"],
            distance=2778,
            handicap="00:14.000000",
            participant="FORTUNA",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_VETERAN,
            club_name="PONTEJOS",
            lane=None,
            series=None,
            laps=["14:27.000000"],
            distance=2778,
            handicap="00:14.000000",
            participant="PONTEJOS",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_VETERAN,
            club_name="BADOK 13",
            lane=None,
            series=None,
            laps=["14:07.410000"],
            distance=2778,
            handicap=None,
            participant="BADOK 13",
            race=_RACE,
            disqualified=False,
        ),
    ]
    _RACE_NAMES = [
        RaceName(
            race_id="getxo",
            name="XIX REGATA DE TRAINERAS DE VETERANOS DE GETXO (29/7/23)",
        ),
        RaceName(
            race_id="plentzia",
            name="V BANDERA KARMENGO AMA. PLENTZIA (17/7/22)",
        ),
        RaceName(
            race_id="fortuna",
            name="XII REGATA DE VETERANOS FORTUNA K. E. (8/5/2023)",
        ),
    ]
