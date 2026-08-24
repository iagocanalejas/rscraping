import os
from datetime import datetime
from pathlib import Path

import pytest
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

FIXTURES_DIR = Path(os.path.join(os.getcwd(), "tests", "fixtures", "html"))


@pytest.fixture
def parser():
    return TrainerasHtmlParser()


def load_selector(filename: str) -> Selector:
    path = FIXTURES_DIR / filename
    return Selector(path.read_text(encoding="utf-8"))


def test_multi_day_race_exception(parser):
    selector = load_selector("traineras_race_double.html")
    with pytest.raises(MultiRaceException):
        parser.parse_race(selector, race_id="1234")


def test_parse_race(parser):
    # race_id=5763
    selector = load_selector("traineras_race.html")
    race = parser.parse_race(selector, race_id="1234")
    assert race is not None

    participants = race.participants
    race.participants = []

    assert race == _RACE
    assert participants == _PARTICIPANTS


def test_parse_race_with_label(parser) -> None:
    # race_id=5706
    selector = load_selector("traineras_race_with_label.html")
    race = parser.parse_race(selector, race_id="5706")
    assert race is not None

    participants = race.participants
    race.participants = []

    assert race == _RACE_LABEL
    assert participants == _PARTICIPANTS_LABEL


def test_parse_race_double(parser) -> None:
    # race_id=4934
    selector = load_selector("traineras_race_double.html")
    races = [
        parser.parse_race(selector, race_id="1234", table=1),
        parser.parse_race(selector, race_id="1234", table=2),
    ]

    for idx, race in enumerate(races):
        assert race is not None
        participants = race.participants
        race.participants = []

        assert race == _RACES_DOUBLE[idx]
        assert participants == _PARTICIPANTS_DOUBLE[idx]


def test_parse_race_double_with_label(parser) -> None:
    # race_id=1625
    selector = load_selector("traineras_race_double_with_label.html")
    races = [
        parser.parse_race(selector, race_id="1234", table=1),
        parser.parse_race(selector, race_id="1234", table=2),
    ]

    for i, race in enumerate(races):
        assert race is not None
        race.participants = []

        assert race == _RACES_DOUBLE_1[i]


def test_parse_race_triple(parser) -> None:
    # race_id=2503
    selector = load_selector("traineras_race_triple.html")
    races = [
        parser.parse_race(selector, race_id="1234", table=1),
        parser.parse_race(selector, race_id="1234", table=2),
        parser.parse_race(selector, race_id="1234", table=3),
    ]

    for idx, race in enumerate(races):
        assert race is not None
        participants = race.participants
        race.participants = []

        assert race == _RACES_TRIPLE[idx]
        assert participants == _PARTICIPANTS_TRIPLE[idx]


def test_parse_race_names(parser) -> None:
    selector = load_selector("traineras_results.html")

    race_names = parser.parse_race_names(selector)
    assert list(race_names) == _RACE_NAMES


def test_parse_race_ids(parser) -> None:
    selector = load_selector("traineras_results.html")

    ids = parser.parse_race_ids(selector)
    assert list(ids) == ["5455", "5456", "5457", "5458", "5535", "5536"]


def test_parse_race_ids_by_days(parser) -> None:
    selector = load_selector("traineras_results.html")

    ids = parser.parse_race_ids_by_days(selector, days=[datetime.strptime("15-01-2023", "%d-%m-%Y")])
    assert list(ids) == ["5455", "5456", "5457", "5458"]


def test_parse_flag_race_ids(parser) -> None:
    selector = load_selector("traineras_flag.html")
    male_ids = parser.parse_flag_race_ids(selector, gender=GENDER_MALE, category=CATEGORY_ABSOLUT)
    female_ids = parser.parse_flag_race_ids(selector, gender=GENDER_FEMALE, category=CATEGORY_VETERAN)

    assert list(male_ids) == ["2476", "2477", "5814"]
    assert list(female_ids) == ["2508", "5815"]


def test_parse_club_race_ids(parser) -> None:
    selector = load_selector("traineras_club.html")
    ids = parser.parse_club_race_ids(selector)
    assert list(ids) == ["4200", "4929", "4931"]


def test_parse_rower_race_ids(parser) -> None:
    selector = load_selector("traineras_rower.html")
    ids = parser.parse_rower_race_ids(selector)
    assert list(ids) == ["732", "3041", "1981", "733", "570", "516", "3309"]


def test_parse_club_details(parser) -> None:
    selector = load_selector("traineras_club_details.html")
    club = parser.parse_club_details(selector)
    assert club == _CLUB


def test_parse_search_flags(parser) -> None:
    selector = load_selector("traineras_search_flags.html")
    urls = parser.parse_searched_flag_urls(selector)
    assert urls == ["https://traineras.es/banderas/104#SM", "https://traineras.es/banderas/679#SF"]


def test_parse_flag_editions(parser) -> None:
    selector = load_selector("traineras_flag_editions.html")
    male_editions = parser.parse_flag_editions(selector, gender=GENDER_MALE, category=CATEGORY_ABSOLUT)
    female_editions = parser.parse_flag_editions(selector, gender=GENDER_FEMALE, category=CATEGORY_ABSOLUT)
    assert list(male_editions) == [(2007, 1), (2008, 2), (2011, 3), (2023, 14)]
    assert list(female_editions) == [(2016, 1), (2017, 2), (2023, 8)]


def test_get_number_of_pages(parser) -> None:
    selector = load_selector("traineras_results.html")
    assert parser.get_number_of_pages(selector) == 1


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
        guest=False,
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
        guest=False,
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
        guest=False,
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
        guest=False,
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
        guest=False,
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
        race_laps=1,
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
            guest=False,
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
            guest=False,
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
            guest=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="C.R. PUEBLA",
            lane=None,
            series=1,
            laps=["21:02.240000"],
            distance=5556,
            handicap=None,
            participant="PUEBLA",
            race=_RACES_DOUBLE[1],
            absent=False,
            retired=False,
            guest=False,
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
        race_notes=(
            "Las dos regatas que se muestran el día 11 correspondían a ligas diferentes, por ese motivo "
            "aparecen separados los resultados, pero los mejores 10 tiempos disputaban la final, "
            "independientemente de la liga de la que formaban parte."
        ),
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
        race_notes=(
            "Las dos regatas que se muestran el día 11 correspondían a ligas diferentes, por ese motivo "
            "aparecen separados los resultados, pero los mejores 10 tiempos disputaban la final, "
            "independientemente de la liga de la que formaban parte."
        ),
        cancelled=False,
    ),
    Race(
        name="BANDERA TERESA HERRERA",
        date="12/08/2012",
        day=1,
        modality=RACE_TRAINERA,
        type=RACE_CONVENTIONAL,
        league=None,
        town="A CORUÑA",
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
        race_notes=(
            "Las dos regatas que se muestran el día 11 correspondían a ligas diferentes, por ese motivo "
            "aparecen separados los resultados, pero los mejores 10 tiempos disputaban la final, "
            "independientemente de la liga de la que formaban parte."
        ),
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
            guest=False,
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
            guest=False,
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
            guest=False,
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
            guest=False,
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
            guest=False,
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
            guest=False,
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
