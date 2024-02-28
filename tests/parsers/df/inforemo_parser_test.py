import os
import unittest

import pandas as pd

from rscraping.data.constants import CATEGORY_ABSOLUT, GENDER_FEMALE, GENDER_MALE, RACE_CONVENTIONAL, RACE_TRAINERA
from rscraping.data.models import Datasource, Participant, Race
from rscraping.parsers.df.inforemo import InforemoDataFrameParser


class TestInforemoParser(unittest.TestCase):
    def setUp(self):
        self.parser = InforemoDataFrameParser(source=Datasource.INFOREMO)
        self.fixtures = os.path.join(os.getcwd(), "fixtures", "df")

    def test_parse_race_from(self):
        header_data = """
        CAMPEONATO GALEGO DE TRAINERAS

        PR ARES
        > 25 XULLO 2023

        maobancofijo X CAMPEONATO FEMENINO
        """
        df = pd.read_hdf(os.path.join(self.fixtures, "inforemo_tabular.h5"), key="data")
        assert isinstance(df, pd.DataFrame)  # needed as 'read_hdf' is returning TableIterator

        races = list(self.parser.parse_races_from(data=df, file_name="inforemo", header=header_data, tabular=df))

        self.assertEqual(len(races), 2)

        for i, race in enumerate(races):
            participants = race.participants
            race.participants = []

            self.assertEqual(race, self._RACES[i])
            self.assertEqual(participants, self._PARTICIPANTS[i])

    _RACES = [
        Race(
            name="CAMPEONATO GALEGO DE TRAINERAS",
            date="25/07/2023",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_CONVENTIONAL,
            league=None,
            town=None,
            organizer=None,
            sponsor=None,
            normalized_names=[("CAMPEONATO GALEGO DE TRAINERAS", None)],
            race_id="inforemo",
            url=None,
            datasource=Datasource.INFOREMO.value,
            gender=GENDER_FEMALE,
            participants=[],
            race_laps=4,
            race_lanes=4,
            cancelled=False,
        ),
        Race(
            name="CAMPEONATO GALEGO DE TRAINERAS",
            date="25/07/2023",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_CONVENTIONAL,
            league=None,
            town=None,
            organizer=None,
            sponsor=None,
            normalized_names=[("CAMPEONATO GALEGO DE TRAINERAS", None)],
            race_id="inforemo",
            url=None,
            datasource=Datasource.INFOREMO.value,
            gender=GENDER_MALE,
            participants=[],
            race_laps=4,
            race_lanes=4,
            cancelled=False,
        ),
    ]

    _PARTICIPANTS = [
        [
            Participant(
                gender=GENDER_FEMALE,
                category=CATEGORY_ABSOLUT,
                club_name="CR CABO DA CRUZ",
                lane=1,
                series=2,
                laps=["00:05:41", "00:11:18", "00:17:34", "00:23:23.250000"],
                distance=5556,
                handicap=None,
                participant="CABO DA CRUZ",
                race=_RACES[0],
                disqualified=False,
                lineup=None,
            ),
            Participant(
                gender=GENDER_FEMALE,
                category=CATEGORY_ABSOLUT,
                club_name="SD TIRAN",
                lane=3,
                series=2,
                laps=["00:05:51", "00:11:33", "00:17:58", "00:23:42.340000"],
                distance=5556,
                handicap=None,
                participant="TIRAN",
                race=_RACES[0],
                disqualified=False,
                lineup=None,
            ),
            Participant(
                gender=GENDER_FEMALE,
                category=CATEGORY_ABSOLUT,
                club_name="CR CHAPELA",
                lane=4,
                series=2,
                laps=["00:05:48", "00:11:35", "00:17:58", "00:23:43.500000"],
                distance=5556,
                handicap=None,
                participant="CHAPELA",
                race=_RACES[0],
                disqualified=False,
                lineup=None,
            ),
        ],
        [
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="CR CABO DA CRUZ",
                lane=2,
                series=3,
                laps=["00:04:58", "00:09:58", "00:15:21", "00:20:20.970000"],
                distance=5556,
                handicap=None,
                participant="CABO DA CRUZ",
                race=_RACES[1],
                disqualified=False,
                lineup=None,
            ),
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="CR ARES",
                lane=4,
                series=3,
                laps=["00:04:59", "00:10:03", "00:15:26", "00:20:25.020000"],
                distance=5556,
                handicap=None,
                participant="ARES",
                race=_RACES[1],
                disqualified=False,
                lineup=None,
            ),
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="CR NARON",
                lane=1,
                series=1,
                laps=["00:05:22", "00:10:44", "00:16:29", "00:21:49.470000"],
                distance=5556,
                handicap=None,
                participant="NARON",
                race=_RACES[1],
                disqualified=False,
                lineup=None,
            ),
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="CM MUGARDOS",
                lane=4,
                series=1,
                laps=["00:05:31", "00:11:06", "00:17:04", "00:22:37.980000"],
                distance=5556,
                handicap=None,
                participant="MUGARDOS",
                race=_RACES[1],
                disqualified=False,
                lineup=None,
            ),
        ],
    ]
