import os
import unittest

from parsel import Selector
from rscraping.data.models import Participant, Race

from rscraping.parsers.html.act import ACTHtmlParser


class TestACTParser(unittest.TestCase):
    def setUp(self):
        self.parser = ACTHtmlParser()
        self.fixtures = os.path.join(os.getcwd(), "fixtures")

    def test_parse_race(self):
        with open(os.path.join(self.fixtures, "act_details.html"), "r") as file:
            race = self.parser.parse_race(
                Selector(file.read()),
                race_id="1234",
                is_female=False,
            )
        if not race:
            raise ValueError(f"unable to parse race")

        participants = race.participants
        race.participants = []

        self.assertEqual(race, self._RACE)
        self.assertEqual(participants, self._PARTICIPANTS)

    def test_parse_race_ids(self):
        with open(os.path.join(self.fixtures, "act_races.html"), "r") as file:
            ids = self.parser.parse_race_ids(Selector(file.read()))

        self.assertEqual(ids, ["1616789082", "1616789390", "1616789420"])

    _RACE = Race(
        name="BANDERA PETRONOR",
        date="17/07/2022",
        edition=39,
        day=1,
        modality="TRAINERA",
        type="CONVENTIONAL",
        league="EUSKO LABEL LIGA",
        town="ZIERBENA BIZKAIA",
        organizer=None,
        trophy_name="BANDERA PETRONOR",
        race_id="1234",
        url=None,
        datasource="act",
        participants=[],
        race_laps=7,
        race_lanes=4,
        cancelled=False,
    )
    _PARTICIPANTS = [
        Participant(
            gender="MALE",
            category="ABSOLUT",
            club_name="GETARIA",
            lane=3,
            series=0,
            laps=["05:03.000000", "09:57.000000", "15:20.000000", "20:09.900000"],
            distance=5556,
            participant="GETARIA",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender="MALE",
            category="ABSOLUT",
            club_name="ZIERBENA BAHIAS DE BIZKAIA",
            lane=4,
            series=0,
            laps=["05:05.000000", "09:59.000000", "15:26.000000", "20:20.980000"],
            distance=5556,
            participant="ZIERBENA",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender="MALE",
            category="ABSOLUT",
            club_name="MATRIX HONDARRIBIA",
            lane=2,
            series=0,
            laps=["04:57.000000", "09:44.000000", "15:05.000000", "19:54.520000"],
            distance=5556,
            participant="HONDARRIBIA",
            race=_RACE,
            disqualified=False,
        ),
    ]
