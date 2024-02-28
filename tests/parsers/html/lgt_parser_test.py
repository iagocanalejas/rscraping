import os
import unittest

from parsel.selector import Selector

from rscraping.data.constants import CATEGORY_ABSOLUT, GENDER_MALE, RACE_CONVENTIONAL, RACE_TRAINERA
from rscraping.data.models import Datasource, Participant, Race, RaceName
from rscraping.parsers.html.lgt import LGTHtmlParser


class TestLGTParser(unittest.TestCase):
    def setUp(self):
        self.parser = LGTHtmlParser()
        self.fixtures = os.path.join(os.getcwd(), "fixtures", "html")

    def test_parse_race(self):
        with (
            open(os.path.join(self.fixtures, "lgt_details.html")) as file,
            open(os.path.join(self.fixtures, "lgt_results.html")) as results,
        ):
            race = self.parser.parse_race(
                Selector(file.read()),
                results_selector=Selector(results.read()),
                race_id="1234",
            )
        if not race:
            raise ValueError("unable to parse race")

        participants = race.participants
        race.participants = []

        self.assertEqual(race, self._RACE)
        self.assertEqual(participants, self._PARTICIPANTS)

    def test_parse_race_ids(self):
        with open(os.path.join(self.fixtures, "lgt_races.html")) as file:
            ids = self.parser.parse_race_ids(Selector(file.read()))

        self.assertEqual(list(ids), ["152", "153", "154"])

    def test_parse_race_names(self):
        with open(os.path.join(self.fixtures, "lgt_races.html")) as file:
            race_names = self.parser.parse_race_names(Selector(file.read()), is_female=False)

        self.assertEqual(list(race_names), self._RACE_NAMES)

    _RACE = Race(
        name="IX BANDEIRA VIRXE DO CARME",
        date="25/07/2020",
        day=1,
        modality=RACE_TRAINERA,
        type=RACE_CONVENTIONAL,
        league="LIGA A",
        town="",
        organizer=None,
        sponsor=None,
        normalized_names=[("BANDEIRA VIRXE DO CARME", 9)],
        race_id="1234",
        url=None,
        datasource=Datasource.LGT.value,
        gender=GENDER_MALE,
        participants=[],
        race_laps=4,
        race_lanes=4,
        cancelled=False,
    )
    _PARTICIPANTS = [
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="CR MUROS",
            lane=4,
            series=1,
            laps=["06:35.000000", "11:59.000000", "19:08.000000", "24:24.970000"],
            distance=5556,
            handicap=None,
            participant="MUROS",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="CR CABO DA CRUZ",
            lane=2,
            series=2,
            laps=["06:11.000000", "11:22.000000", "17:49.000000", "22:55.920000"],
            distance=5556,
            handicap=None,
            participant="CABO DA CRUZ",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="SD TIRÁN - PEREIRA",
            lane=4,
            series=2,
            laps=["05:59.000000", "11:02.000000", "17:21.000000", "22:31.390000"],
            distance=5556,
            handicap=None,
            participant="TIRÁN",
            race=_RACE,
            disqualified=False,
        ),
    ]
    _RACE_NAMES = [
        RaceName(race_id="152", name="XXVIII BANDEIRA TRAIÑEIRAS CONCELLO DE BUEU"),
        RaceName(race_id="153", name="I BANDEIRA CONCELLO AS PONTES B"),
        RaceName(race_id="154", name="I BANDEIRA CONCELLO AS PONTES F"),
    ]
