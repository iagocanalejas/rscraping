import os
import unittest

from parsel import Selector
from rscraping.data.constants import GENDER_MALE
from rscraping.data.models import Participant, Race

from rscraping.parsers.html.lgt import LGTHtmlParser


class TestLGTParser(unittest.TestCase):
    def setUp(self):
        self.parser = LGTHtmlParser()
        self.fixtures = os.path.join(os.getcwd(), "fixtures")

    def test_parse_race(self):
        with (
            open(os.path.join(self.fixtures, "lgt_details.html"), "r") as file,
            open(os.path.join(self.fixtures, "lgt_results.html"), "r") as results,
        ):
            race = self.parser.parse_race(
                Selector(file.read()),
                Selector(results.read()),
                race_id="1234",
            )
        if not race:
            raise ValueError(f"unable to parse race")

        participants = race.participants
        race.participants = []

        self.assertEqual(race, self._RACE)
        self.assertEqual(participants, self._PARTICIPANTS)

    _RACE = Race(
        name="BANDEIRA VIRXE DO CARME",
        date="25/07/2020",
        edition=9,
        day=1,
        modality="TRAINERA",
        type="CONVENTIONAL",
        league="LIGA A",
        town="",
        organizer=None,
        normalized_name="BANDEIRA VIRXE DO CARME",
        race_id="1234",
        url=None,
        datasource="arc",
        gender=GENDER_MALE,
        participants=[],
        race_laps=4,
        race_lanes=4,
        cancelled=False,
    )
    _PARTICIPANTS = [
        Participant(
            gender="MALE",
            category="ABSOLUT",
            club_name="CR MUROS",
            lane=4,
            series=0,
            laps=["06:35.000000", "11:59.000000", "19:08.000000", "24:24.970000"],
            distance=5556,
            participant="MUROS",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender="MALE",
            category="ABSOLUT",
            club_name="CR CABO DA CRUZ",
            lane=2,
            series=0,
            laps=["06:11.000000", "11:22.000000", "17:49.000000", "22:55.920000"],
            distance=5556,
            participant="CABO DA CRUZ",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender="MALE",
            category="ABSOLUT",
            club_name="SD TIRÁN - PEREIRA",
            lane=4,
            series=0,
            laps=["05:59.000000", "11:02.000000", "17:21.000000", "22:31.390000"],
            distance=5556,
            participant="TIRÁN",
            race=_RACE,
            disqualified=False,
        ),
    ]
