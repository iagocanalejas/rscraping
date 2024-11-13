import os
import unittest

import pandas as pd

from rscraping.data.constants import CATEGORY_ABSOLUT, GENDER_MALE, RACE_CONVENTIONAL, RACE_TIME_TRIAL, RACE_TRAINERA
from rscraping.data.models import Datasource, Participant, Race, RaceName
from rscraping.parsers.df import TabularDataFrameParser


class TestTabularDataParser(unittest.TestCase):
    def setUp(self):
        self.parser = TabularDataFrameParser()
        self.fixtures = os.path.join(os.getcwd(), "tests", "fixtures", "df")

    def test_parse_race(self):
        df = pd.read_hdf(os.path.join(self.fixtures, "gdrive_tabular.h5"), key="data")
        assert isinstance(df, pd.DataFrame)  # needed as 'read_hdf' is returning TableIterator

        race_row = df.iloc[0]
        race = self.parser.parse_race(race_row, is_female=False, url="test_url")

        if not race:
            self.assertIsNotNone(race)
            return

        participants = race.participants
        race.participants = []

        self.assertEqual(race, self._RACE)
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0], self._PARTICIPANT)

    def test_parse_races(self):
        df = pd.read_hdf(os.path.join(self.fixtures, "gdrive_tabular.h5"), key="data")
        assert isinstance(df, pd.DataFrame)

        races = self.parser.parse_races(df, is_female=False, url="test_url")
        for i, race in enumerate(races):
            participants = race.participants
            race.participants = []

            self.assertEqual(race, self._RACES[i])
            self.assertEqual(len(participants), 1)
            self.assertEqual(participants[0], self._PARTICIPANTS[i])

    def test_parse_race_ids(self):
        df = pd.read_hdf(os.path.join(self.fixtures, "gdrive_tabular.h5"), key="data")
        assert isinstance(df, pd.DataFrame)

        races = self.parser.parse_race_ids(df, 2011)
        self.assertEqual(list(races), ["1"])

        races = self.parser.parse_race_ids(df, 2012)
        self.assertEqual(list(races), [])

    def test_parse_race_names(self):
        df = pd.read_hdf(os.path.join(self.fixtures, "gdrive_tabular.h5"), key="data")
        assert isinstance(df, pd.DataFrame)

        races = self.parser.parse_race_names(df, 2011)
        self.assertEqual(list(races), [RaceName(race_id="1", name="REGATA CARITAS VILAXOAN")])

        races = self.parser.parse_race_names(df, 2012)
        self.assertEqual(list(races), [])

    _RACE = Race(
        name="REGATA CARITAS VILAXOAN",
        date="18/12/2011",
        day=1,
        modality=RACE_TRAINERA,
        type=RACE_CONVENTIONAL,
        league=None,
        town=None,
        organizer="CLUB REMO VILAXOAN",
        sponsor=None,
        normalized_names=[("REGATA CARITAS VILAXOAN", 1)],
        race_ids=["1"],
        url="test_url",
        datasource=Datasource.TABULAR.value,
        gender=GENDER_MALE,
        category=CATEGORY_ABSOLUT,
        participants=[],
        race_laps=None,
        race_lanes=None,
        cancelled=False,
    )
    _PARTICIPANT = Participant(
        gender=GENDER_MALE,
        category=CATEGORY_ABSOLUT,
        club_name="CLUB REMO PUEBLA",
        lane=None,
        series=None,
        laps=["21:04.470000"],
        distance=5556,
        handicap=None,
        participant="PUEBLA",
        race=_RACE,
        absent=False,
        retired=False,
        guest=False,
    )

    _RACES = [
        Race(
            name="REGATA CARITAS VILAXOAN",
            date="18/12/2011",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_CONVENTIONAL,
            league=None,
            town=None,
            organizer="CLUB REMO VILAXOAN",
            sponsor=None,
            normalized_names=[("REGATA CARITAS VILAXOAN", 1)],
            race_ids=["1"],
            url="test_url",
            datasource=Datasource.TABULAR.value,
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_laps=None,
            race_lanes=None,
            cancelled=False,
        ),
        Race(
            name="TROFEO TERESA HERRERA (CLASIFICATORIA)",
            date="10/08/2013",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_TIME_TRIAL,
            league=None,
            town=None,
            organizer="FEDERACIÓN GALEGA DE REMO",
            sponsor=None,
            normalized_names=[("TROFEO TERESA HERRERA (CLASIFICATORIA)", 28)],
            race_ids=["2"],
            url="test_url",
            datasource=Datasource.TABULAR.value,
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_laps=4,
            race_lanes=1,
            cancelled=False,
        ),
        Race(
            name="BANDEIRA MASCULINA DEPUTACIÓN DA CORUÑA (RIVEIRA)",
            date="02/08/2015",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_CONVENTIONAL,
            league=None,
            town="RIVEIRA",
            organizer="FEDERACIÓN GALEGA DE REMO",
            sponsor=None,
            normalized_names=[("BANDEIRA MASCULINA DEPUTACIÓN DA CORUÑA", 25)],
            race_ids=["3"],
            url="test_url",
            datasource=Datasource.TABULAR.value,
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_laps=6,
            race_lanes=None,
            cancelled=False,
        ),
        Race(
            name="BANDEIRA SALGADO CONGELADOS PERILLO",
            date="01/07/2017",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_CONVENTIONAL,
            league="LIGA A",
            town=None,
            organizer="CLUB DE REGATAS PERILLO",
            sponsor="SALGADO CONGELADOS",
            normalized_names=[("BANDEIRA SALGADO CONGELADOS", 6)],
            race_ids=["4"],
            url="test_url",
            datasource=Datasource.TABULAR.value,
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_laps=4,
            race_lanes=4,
            cancelled=False,
        ),
    ]

    _PARTICIPANTS = [
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="CLUB REMO PUEBLA",
            lane=None,
            series=None,
            laps=["21:04.470000"],
            distance=5556,
            handicap=None,
            participant="PUEBLA",
            race=_RACES[0],
            absent=False,
            retired=False,
            guest=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="CLUB REMO PUEBLA",
            lane=1,
            series=None,
            laps=["23:52.280000"],
            distance=5628,
            handicap=None,
            participant="PUEBLA",
            race=_RACES[1],
            absent=False,
            retired=False,
            guest=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="CLUB REMO PUEBLA",
            lane=None,
            series=None,
            laps=["21:31.790000"],
            distance=5800,
            handicap=None,
            participant="PUEBLA",
            race=_RACES[2],
            absent=False,
            retired=False,
            guest=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="CLUB REMO PUEBLA",
            lane=None,
            series=None,
            laps=["19:16.640000"],
            distance=5556,
            handicap=None,
            participant="PUEBLA",
            race=_RACES[3],
            absent=False,
            retired=False,
            guest=False,
        ),
    ]
