import os
from datetime import datetime
from pathlib import Path

import pytest
from parsel.selector import Selector

from rscraping.data.constants import (
    CATEGORY_ABSOLUT,
    DATE_FORMAT,
    GENDER_MALE,
    RACE_CONVENTIONAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Datasource, Participant, Race, RaceName
from rscraping.parsers.html.lgt import LGTHtmlParser

FIXTURES_DIR = Path(os.path.join(os.getcwd(), "tests", "fixtures", "html"))


@pytest.fixture
def parser():
    return LGTHtmlParser()


def load_selector(filename: str) -> Selector:
    path = FIXTURES_DIR / filename
    return Selector(path.read_text(encoding="utf-8"))


def test_parse_race(parser):
    selector = load_selector("lgt_details.html")
    results = load_selector("lgt_results.html")
    race = parser.parse_race(selector, race_id="1234", results_selector=results)
    assert race is not None

    participants = race.participants
    race.participants = []

    assert race == _RACE
    assert participants == _PARTICIPANTS


def test_parse_race_names(parser):
    selector = load_selector("lgt_races.html")

    race_names = parser.parse_race_names(selector, is_female=False)
    assert list(race_names) == _RACE_NAMES


def test_parse_race_ids(parser):
    selector = load_selector("lgt_races.html")

    ids = parser.parse_race_ids(selector)
    assert list(ids) == ["152", "153", "154"]


def test_parse_race_ids_by_days(parser):
    selector = load_selector("lgt_calendar.html")

    ids = parser.parse_race_ids_by_days(selector, days=[datetime.strptime("03/08/2024", DATE_FORMAT)])
    assert list(ids) == ["209", "210"]


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
    race_ids=["1234"],
    url=None,
    datasource=Datasource.LGT.value,
    gender=GENDER_MALE,
    category=CATEGORY_ABSOLUT,
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
        absent=False,
        retired=False,
        guest=False,
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
        absent=False,
        retired=False,
        guest=False,
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
        absent=False,
        retired=False,
        guest=False,
    ),
]

_RACE_NAMES = [
    RaceName(race_id="152", name="XXVIII BANDEIRA TRAIÑEIRAS CONCELLO DE BUEU"),
    RaceName(race_id="153", name="I BANDEIRA CONCELLO AS PONTES B"),
    RaceName(race_id="154", name="I BANDEIRA CONCELLO AS PONTES F"),
]
