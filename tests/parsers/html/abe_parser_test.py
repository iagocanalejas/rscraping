import os
import unittest

from parsel import Selector

from rscraping.data.models import Participant, Race, RaceName
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

        self.assertEqual(ids, ["getxo", "plentzia", "fortuna"])

    def test_parse_race_names(self):
        with open(os.path.join(self.fixtures, "abe_races.html")) as file:
            race_names = self.parser.parse_race_names(Selector(file.read()), is_female=False)

        self.assertEqual(race_names, self._RACE_NAMES)

    _RACE = Race(
        name="XIII BANDERA CRV PONTEJOS (3/6/2023)",
        date="03/06/2023",
        day=1,
        modality="TRAINERA",
        type="CONVENTIONAL",
        league="ARRAUNLARI BETERANOEN ELKARTEA",
        town=None,
        organizer=None,
        sponsor=None,
        normalized_names=[("BANDERA CRV PONTEJOS", 13)],
        race_id="1234",
        url=None,
        datasource="abe",
        gender="MALE",
        participants=[],
        race_laps=None,
        race_lanes=None,
        cancelled=False,
    )
    _PARTICIPANTS = [
        Participant(
            gender="MALE",
            category="ABSOLUT",
            club_name="FORTUNA",
            lane=None,
            series=None,
            laps=["13:57.020000"],
            distance=2778,
            handicap=None,
            participant="FORTUNA",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender="MALE",
            category="ABSOLUT",
            club_name="PONTEJOS",
            lane=None,
            series=None,
            laps=["14:06.890000"],
            distance=2778,
            handicap=None,
            participant="PONTEJOS",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender="MALE",
            category="ABSOLUT",
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
