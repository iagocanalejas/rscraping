import os
import unittest

import pandas as pd

from rscraping.data.constants import CATEGORY_ABSOLUT, GENDER_MALE, RACE_CONVENTIONAL, RACE_TIME_TRIAL, RACE_TRAINERA
from rscraping.data.models import Datasource, Participant, Race
from rscraping.parsers.df import TabularDataFrameParser


class TestTabularDataParser(unittest.TestCase):
    def setUp(self):
        self.parser = TabularDataFrameParser()
        self.fixtures = os.path.join(os.getcwd(), "fixtures", "df")

    def test_parse_race_series(self):
        df = pd.read_hdf(os.path.join(self.fixtures, "gdrive_tabular.h5"), key="data")
        assert isinstance(df, pd.DataFrame)  # needed as 'read_hdf' is returning TableIterator

        race_row = df.iloc[0]
        race = self.parser.parse_race_serie(race_row, is_female=False)

        if not race:
            self.assertIsNotNone(race)
            return

        participants = race.participants
        race.participants = []

        self.assertEqual(race, self._RACE)
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0], self._PARTICIPANT)

    def test_parse_races_from(self):
        df = pd.read_hdf(os.path.join(self.fixtures, "gdrive_tabular.h5"), key="data")
        assert isinstance(df, pd.DataFrame)

        races = self.parser.parse_races_from(df, is_female=False)
        for i, race in enumerate(races):
            participants = race.participants
            race.participants = []

            self.assertEqual(race, self._RACES[i])
            self.assertEqual(len(participants), 1)
            self.assertEqual(participants[0], self._PARTICIPANTS[i])

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
        normalized_names=[("REGATA CARITAS VILAXOAN", None)],
        race_ids=["1"],
        url=None,
        datasource=Datasource.TABULAR.value,
        gender=GENDER_MALE,
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
        disqualified=False,
        lineup=None,
        race=_RACE,
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
            normalized_names=[("REGATA CARITAS VILAXOAN", None)],
            race_ids=["1"],
            url=None,
            datasource=Datasource.TABULAR.value,
            gender=GENDER_MALE,
            participants=[],
            race_laps=None,
            race_lanes=None,
            cancelled=False,
        ),
        Race(
            name="TROFEO TERESA HERRERA (CLASIFICATORIA)",
            date="27/06/2015",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_TIME_TRIAL,
            league=None,
            town=None,
            organizer="FEDERACIÓN GALEGA DE REMO",
            sponsor=None,
            normalized_names=[("TROFEO TERESA HERRERA", None)],
            race_ids=["2"],
            url=None,
            datasource=Datasource.TABULAR.value,
            gender=GENDER_MALE,
            participants=[],
            race_laps=None,
            race_lanes=None,
            cancelled=False,
        ),
        Race(
            name="BANDEIRA MASCULINA DEPUTACIÓN DA CORUÑA (RIVEIRA)",
            date="30/07/2016",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_CONVENTIONAL,
            league=None,
            town="RIVEIRA",
            organizer="FEDERACIÓN GALEGA DE REMO",
            sponsor=None,
            normalized_names=[("BANDEIRA MASCULINA DEPUTACIÓN DA CORUÑA", None)],
            race_ids=["3"],
            url=None,
            datasource=Datasource.TABULAR.value,
            gender=GENDER_MALE,
            participants=[],
            race_laps=None,
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
            sponsor=None,
            normalized_names=[("BANDEIRA CONGELADOS PERILLO", None)],
            race_ids=["4"],
            url=None,
            datasource=Datasource.TABULAR.value,
            gender=GENDER_MALE,
            participants=[],
            race_laps=None,
            race_lanes=None,
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
            disqualified=False,
            lineup=None,
            race=_RACES[0],
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="CLUB REMO PUEBLA",
            lane=None,
            series=None,
            laps=["23:52.280000"],
            distance=5556,
            handicap=None,
            participant="PUEBLA",
            disqualified=False,
            lineup=None,
            race=_RACES[1],
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="CLUB REMO PUEBLA",
            lane=None,
            series=None,
            laps=["21:31.790000"],
            distance=5556,
            handicap=None,
            participant="PUEBLA",
            disqualified=False,
            lineup=None,
            race=_RACES[2],
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
            disqualified=False,
            lineup=None,
            race=_RACES[3],
        ),
    ]
