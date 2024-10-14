import os
import unittest
from datetime import datetime

from parsel.selector import Selector

from rscraping.data.constants import (
    CATEGORY_ABSOLUT,
    CATEGORY_VETERAN,
    GENDER_FEMALE,
    GENDER_MALE,
    RACE_CONVENTIONAL,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Club, Datasource, Participant, Race, RaceName
from rscraping.parsers.html.traineras import MultiRaceException, TrainerasHtmlParser


class TestTrainerasParser(unittest.TestCase):
    def setUp(self):
        self.parser = TrainerasHtmlParser()
        self.fixtures = os.path.join(os.getcwd(), "tests", "fixtures", "html")

    def test_multi_day_race_exception(self):
        with open(os.path.join(self.fixtures, "traineras_race_double.html")) as file:
            with self.assertRaises(MultiRaceException):
                self.parser.parse_race(
                    Selector(file.read()),
                    race_id="1234",
                )

    def test_parse_race(self):
        # race_id=5763
        with open(os.path.join(self.fixtures, "traineras_race.html")) as file:
            selector = Selector(file.read())
            race = self.parser.parse_race(selector, race_id="1234")
        assert race is not None

        participants = race.participants
        race.participants = []

        self.assertEqual(race, self._RACE)
        self.assertEqual(participants, self._PARTICIPANTS)

    def test_parse_race_with_label(self):
        # race_id=5706
        with open(os.path.join(self.fixtures, "traineras_race_with_label.html")) as file:
            selector = Selector(file.read())
            race = self.parser.parse_race(selector, race_id="5706")
        assert race is not None

        participants = race.participants
        race.participants = []

        self.assertEqual(race, self._RACE_LABEL)
        self.assertEqual(participants, self._PARTICIPANTS_LABEL)

    def test_parse_race_double(self):
        # race_id=4934
        with open(os.path.join(self.fixtures, "traineras_race_double.html")) as file:
            selector = Selector(file.read())
            races = [
                self.parser.parse_race(selector, race_id="1234", table=1),
                self.parser.parse_race(selector, race_id="1234", table=2),
            ]

        for idx, race in enumerate(races):
            assert race is not None
            participants = race.participants
            race.participants = []

            self.assertEqual(race, self._RACES_DOUBLE[idx])
            self.assertEqual(participants, self._PARTICIPANTS_DOUBLE[idx])

    def test_parse_race_double_1(self):
        # race_id=1625
        with open(os.path.join(self.fixtures, "traineras_race_double_1.html")) as file:
            selector = Selector(file.read())
            races = [
                self.parser.parse_race(selector, race_id="1234", table=1),
                self.parser.parse_race(selector, race_id="1234", table=2),
            ]

        self.assertEqual(len(races), 2)
        for idx, race in enumerate(races):
            assert race is not None
            race.participants = []

            self.assertEqual(race, self._RACES_DOUBLE_1[idx])

    def test_parse_race_triple(self):
        # race_id=2503
        with open(os.path.join(self.fixtures, "traineras_race_triple.html")) as file:
            selector = Selector(file.read())
            races = [
                self.parser.parse_race(selector, race_id="1234", table=1),
                self.parser.parse_race(selector, race_id="1234", table=2),
                self.parser.parse_race(selector, race_id="1234", table=3),
            ]

        for idx, race in enumerate(races):
            assert race is not None
            participants = race.participants
            race.participants = []

            self.assertEqual(race, self._RACES_TRIPLE[idx])
            self.assertEqual(participants, self._PARTICIPANTS_TRIPLE[idx])

    def test_parse_race_names(self):
        with open(os.path.join(self.fixtures, "traineras_results.html")) as file:
            data = file.read()

        race_names = self.parser.parse_race_names(Selector(data))
        self.assertEqual(list(race_names), self._RACE_NAMES)

    def test_parse_race_ids(self):
        with open(os.path.join(self.fixtures, "traineras_results.html")) as file:
            data = Selector(file.read())

        ids = self.parser.parse_race_ids(data)
        self.assertEqual(list(ids), ["5455", "5456", "5457", "5458", "5535", "5536"])

    def test_parse_race_ids_by_days(self):
        with open(os.path.join(self.fixtures, "traineras_results.html")) as file:
            data = Selector(file.read())

        ids = self.parser.parse_race_ids_by_days(data, days=[datetime.strptime("15-01-2023", "%d-%m-%Y")])
        self.assertEqual(list(ids), ["5455", "5456", "5457", "5458"])

    def test_parse_flag_race_ids(self):
        with open(os.path.join(self.fixtures, "traineras_flag.html")) as file:
            selector = Selector(file.read())
            male_ids = self.parser.parse_flag_race_ids(selector, gender=GENDER_MALE, category=CATEGORY_ABSOLUT)
            female_ids = self.parser.parse_flag_race_ids(selector, gender=GENDER_FEMALE, category=CATEGORY_VETERAN)
        self.assertEqual(list(male_ids), ["2476", "2477", "5814"])
        self.assertEqual(list(female_ids), ["2508", "5815"])

    def test_parse_club_race_ids(self):
        with open(os.path.join(self.fixtures, "traineras_club.html")) as file:
            ids = self.parser.parse_club_race_ids(Selector(file.read()))
        self.assertEqual(list(ids), ["4200", "4929", "4931"])

    def test_parse_rower_race_ids(self):
        with open(os.path.join(self.fixtures, "traineras_rower.html")) as file:
            ids = self.parser.parse_rower_race_ids(Selector(file.read()))
        self.assertEqual(list(ids), ["732", "3041", "1981", "733", "570", "516", "3309"])

    def test_parse_club_details(self):
        with open(os.path.join(self.fixtures, "traineras_club_details.html")) as file:
            club = self.parser.parse_club_details(Selector(file.read()))
        self.assertEqual(club, self._CLUB)

    def test_parse_search_flags(self):
        with open(os.path.join(self.fixtures, "traineras_search_flags.html")) as file:
            urls = self.parser.parse_searched_flag_urls(Selector(file.read()))
        self.assertEqual(urls, ["https://traineras.es/banderas/104#SM", "https://traineras.es/banderas/679#SF"])

    def test_parse_flag_editions(self):
        with open(os.path.join(self.fixtures, "traineras_flag_editions.html")) as file:
            content = Selector(file.read())
            male_editions = self.parser.parse_flag_editions(content, gender=GENDER_MALE, category=CATEGORY_ABSOLUT)
            female_editions = self.parser.parse_flag_editions(content, gender=GENDER_FEMALE, category=CATEGORY_ABSOLUT)
        self.assertEqual(list(male_editions), [(2007, 1), (2008, 2), (2011, 3), (2023, 14)])
        self.assertEqual(list(female_editions), [(2016, 1), (2017, 2), (2023, 8)])

    def test_get_number_of_pages(self):
        with open(os.path.join(self.fixtures, "traineras_results.html")) as file:
            self.assertEqual(self.parser.get_number_of_pages(Selector(file.read())), 1)

    _RACE = Race(
        name="BANDERA CONCELLO DE POBRA",
        date="22/07/2023",
        day=1,
        modality=RACE_TRAINERA,
        type=RACE_CONVENTIONAL,
        league=None,
        town="A POBRA DO CARAMIÑAL",
        organizer=None,
        sponsor=None,
        normalized_names=[("BANDERA CONCELLO DE POBRA", None)],
        race_ids=["1234"],
        url=None,
        datasource=Datasource.TRAINERAS.value.lower(),
        gender=GENDER_MALE,
        category=CATEGORY_ABSOLUT,
        participants=[],
        race_laps=4,
        race_lanes=2,
        cancelled=False,
    )

    _PARTICIPANTS = [
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="C.R. ARES",
            lane=3,
            series=3,
            laps=["02:57.000000", "06:22.000000", "09:37.000000", "19:58.590000"],
            distance=5556,
            handicap=None,
            participant="ARES",
            race=_RACE,
            absent=False,
            retired=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="C.M. BUEU",
            lane=2,
            series=3,
            laps=["02:56.000000", "06:26.000000", "09:41.000000", "20:07.110000"],
            distance=5556,
            handicap=None,
            participant="BUEU",
            race=_RACE,
            absent=False,
            retired=False,
        ),
    ]

    _RACE_LABEL = Race(
        name="CAMPEONATO DE CANTABRIA",
        date="02/07/2023",
        day=1,
        modality=RACE_TRAINERA,
        type=RACE_CONVENTIONAL,
        league=None,
        town="LAREDO",
        organizer=None,
        sponsor=None,
        normalized_names=[("CAMPEONATO DE CANTABRIA", None)],
        race_ids=["5706"],
        url=None,
        datasource=Datasource.TRAINERAS.value.lower(),
        gender=GENDER_MALE,
        category=CATEGORY_ABSOLUT,
        participants=[],
        race_laps=4,
        race_lanes=3,
        cancelled=False,
    )

    _PARTICIPANTS_LABEL = [
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="C.R. CAMARGO",
            lane=2,
            series=2,
            laps=["05:13.000000", "10:16.000000", "15:52.000000", "20:51.140000"],
            distance=5556,
            handicap=None,
            participant="CAMARGO",
            race=_RACE_LABEL,
            absent=False,
            retired=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="S.D.R. PEDREÑA",
            lane=1,
            series=2,
            laps=["05:10.000000", "10:18.000000", "16:02.000000", "21:13.360000"],
            distance=5556,
            handicap=None,
            participant="PEDREÑA",
            race=_RACE_LABEL,
            absent=False,
            retired=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="S.D.R. ASTILLERO",
            lane=4,
            series=2,
            laps=["05:23.000000", "10:39.000000", "16:29.000000", "21:41.170000"],
            distance=5556,
            handicap=None,
            participant="ASTILLERO",
            race=_RACE_LABEL,
            absent=False,
            retired=False,
        ),
    ]

    _RACES_DOUBLE = [
        Race(
            name="BANDERA CONCELLO DE POBRA",
            date="22/08/2020",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_CONVENTIONAL,
            league=None,
            town="A POBRA DO CARAMIÑAL",
            organizer=None,
            sponsor=None,
            normalized_names=[("BANDERA CONCELLO DE POBRA", None)],
            race_ids=["1234"],
            url=None,
            datasource=Datasource.TRAINERAS.value.lower(),
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_laps=4,
            race_lanes=2,
            cancelled=False,
        ),
        Race(
            name="BANDERA CONCELLO DE POBRA",
            date="23/08/2020",
            day=2,
            modality=RACE_TRAINERA,
            type=RACE_CONVENTIONAL,
            league=None,
            town="A POBRA DO CARAMIÑAL",
            organizer=None,
            sponsor=None,
            normalized_names=[("BANDERA CONCELLO DE POBRA", None)],
            race_ids=["1234"],
            url=None,
            datasource=Datasource.TRAINERAS.value.lower(),
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_laps=4,
            race_lanes=2,
            cancelled=False,
        ),
    ]

    _PARTICIPANTS_DOUBLE = [
        [
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="C.C.D. CESANTES",
                lane=1,
                series=2,
                laps=["03:11.000000", "10:16.000000", "17:32.000000", "21:07.770000"],
                distance=5556,
                handicap=None,
                participant="CESANTES",
                race=_RACES_DOUBLE[0],
                absent=False,
                retired=False,
            ),
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="C.R. PUEBLA",
                lane=2,
                series=2,
                laps=["03:06.000000", "10:11.000000", "17:29.000000", "21:08.060000"],
                distance=5556,
                handicap=None,
                participant="PUEBLA",
                race=_RACES_DOUBLE[0],
                absent=False,
                retired=False,
            ),
        ],
        [
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="C.C.D. CESANTES",
                lane=None,
                series=1,
                laps=["20:49.180000"],
                distance=5556,
                handicap=None,
                participant="CESANTES",
                race=_RACES_DOUBLE[1],
                absent=False,
                retired=False,
            ),
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="C.R. PUEBLA",
                lane=None,
                series=1,
                laps=["03:21.000000", "10:30.000000", "17:47.000000", "21:02.240000"],
                distance=5556,
                handicap=None,
                participant="PUEBLA",
                race=_RACES_DOUBLE[1],
                absent=False,
                retired=False,
            ),
        ],
    ]

    _RACES_DOUBLE_1 = [
        Race(
            name="BANDERA DE SANTANDER",
            date="25/08/1979",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_TIME_TRIAL,
            league=None,
            town="SANTANDER",
            organizer=None,
            sponsor=None,
            normalized_names=[("BANDERA DE SANTANDER", None)],
            race_ids=["1234"],
            url=None,
            datasource=Datasource.TRAINERAS.value.lower(),
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_notes=None,
            race_laps=2,
            race_lanes=1,
            cancelled=True,
        ),
        Race(
            name="BANDERA DE SANTANDER",
            date="26/08/1979",
            day=2,
            modality=RACE_TRAINERA,
            type=RACE_TIME_TRIAL,
            league=None,
            town="",
            organizer=None,
            sponsor=None,
            normalized_names=[("BANDERA DE SANTANDER", None)],
            race_ids=["1234"],
            url=None,
            datasource=Datasource.TRAINERAS.value.lower(),
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_notes=None,
            race_laps=4,
            race_lanes=1,
            cancelled=True,
        ),
    ]

    _RACES_TRIPLE = [
        Race(
            name="BANDERA TERESA HERRERA",
            date="11/08/2012",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_TIME_TRIAL,
            league=None,
            town="A CORUÑA",
            organizer=None,
            sponsor=None,
            normalized_names=[("TROFEO TERESA HERRERA (CLASIFICATORIA)", None)],
            race_ids=["1234"],
            url=None,
            datasource=Datasource.TRAINERAS.value.lower(),
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_laps=2,
            race_lanes=1,
            cancelled=False,
        ),
        Race(
            name="BANDERA TERESA HERRERA",
            date="11/08/2012",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_TIME_TRIAL,
            league=None,
            town="A CORUÑA",
            organizer=None,
            sponsor=None,
            normalized_names=[("TROFEO TERESA HERRERA (CLASIFICATORIA)", None)],
            race_ids=["1234"],
            url=None,
            datasource=Datasource.TRAINERAS.value.lower(),
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_laps=2,
            race_lanes=1,
            cancelled=False,
        ),
        Race(
            name="BANDERA TERESA HERRERA",
            date="12/08/2012",
            day=1,
            modality=RACE_TRAINERA,
            type=RACE_CONVENTIONAL,
            league=None,
            town="",
            organizer=None,
            sponsor=None,
            normalized_names=[("TROFEO TERESA HERRERA", None)],
            race_ids=["1234"],
            url=None,
            datasource=Datasource.TRAINERAS.value.lower(),
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            participants=[],
            race_laps=2,
            race_lanes=2,
            cancelled=False,
        ),
    ]

    _PARTICIPANTS_TRIPLE = [
        [
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="C.R. MECOS",
                lane=1,
                series=1,
                laps=["11:02.000000", "22:09.350000"],
                distance=5556,
                handicap=None,
                participant="MECOS",
                race=_RACES_TRIPLE[0],
                absent=False,
                retired=False,
            ),
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="C.R. PERILLO",
                lane=1,
                series=1,
                laps=["11:05.000000", "22:20.660000"],
                distance=5556,
                handicap=None,
                participant="PERILLO",
                race=_RACES_TRIPLE[0],
                absent=False,
                retired=False,
            ),
        ],
        [
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="S.D. SAMERTOLAMEU",
                lane=1,
                series=1,
                laps=["10:36.000000", "21:06.790000"],
                distance=5556,
                handicap=None,
                participant="SAMERTOLAMEU",
                race=_RACES_TRIPLE[1],
                absent=False,
                retired=False,
            ),
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="AMEGROVE C.R.",
                lane=1,
                series=1,
                laps=["10:36.000000", "21:11.320000"],
                distance=5556,
                handicap=None,
                participant="AMEGROVE",
                race=_RACES_TRIPLE[1],
                absent=False,
                retired=False,
            ),
        ],
        [
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="AMEGROVE C.R.",
                lane=2,
                series=2,
                laps=["09:56.000000", "20:01.820000"],
                distance=5556,
                handicap=None,
                participant="AMEGROVE",
                race=_RACES_TRIPLE[2],
                absent=False,
                retired=False,
            ),
            Participant(
                gender=GENDER_MALE,
                category=CATEGORY_ABSOLUT,
                club_name="S.D. SAMERTOLAMEU",
                lane=3,
                series=2,
                laps=["09:56.000000", "20:10.990000"],
                distance=5556,
                handicap=None,
                participant="SAMERTOLAMEU",
                race=_RACES_TRIPLE[2],
                absent=False,
                retired=False,
            ),
        ],
    ]

    _RACE_NAMES = [
        RaceName(race_id="5455", name="MEMORIAL PEPE O RUSO"),
        RaceName(race_id="5456", name="MEMORIAL PEPE O RUSO"),
        RaceName(race_id="5457", name="MEMORIAL PEPE O RUSO"),
        RaceName(race_id="5458", name="MEMORIAL PEPE O RUSO"),
        RaceName(race_id="5535", name="MEMORIAL AURORA TRUEBA"),
        RaceName(race_id="5536", name="MEMORIAL AURORA TRUEBA"),
    ]

    _CLUB = Club(name="ZUMAIA A.E.", normalized_name="ZUMAIA", datasource="traineras", founding_year="1975")
