import os
from datetime import datetime
from pathlib import Path

import pytest
from parsel.selector import Selector

from rscraping.data.constants import (
    CATEGORY_ABSOLUT,
    GENDER_MALE,
    RACE_TIME_TRIAL,
    RACE_TRAINERA,
)
from rscraping.data.models import Datasource, Participant, Race, RaceName
from rscraping.parsers.html.arc import ARCHtmlParser

FIXTURES_DIR = Path(os.path.join(os.getcwd(), "tests", "fixtures", "html"))


@pytest.fixture
def parser():
    return ARCHtmlParser()


def load_selector(filename: str) -> Selector:
    path = FIXTURES_DIR / filename
    return Selector(path.read_text(encoding="utf-8"))


def test_parse_race(parser):
    selector = load_selector("arc_details.html")
    race = parser.parse_race(selector, race_id="1234", is_female=False)
    assert race is not None

    participants = race.participants
    race.participants = []

    assert race == _RACE
    assert participants == _PARTICIPANTS


def test_parse_race_names(parser):
    selector = load_selector("arc_races.html")

    race_names = parser.parse_race_names(selector, is_female=False)
    assert list(race_names) == _RACE_NAMES


def test_parse_race_ids(parser):
    selector = load_selector("arc_races.html")

    ids = parser.parse_race_ids(selector)
    assert list(ids) == ["446", "474", "475"]


def test_parse_race_ids_by_days(parser):
    selector = load_selector("arc_races.html")

    ids = parser.parse_race_ids_by_days(selector, days=[datetime.strptime("19 JUNE 2009", "%d %B %Y")])
    assert list(ids) == ["446"]


_RACE = Race(
    name="XVII BANDERA RIA DEL ASON",
    date="22/08/2009",
    day=1,
    modality=RACE_TRAINERA,
    type=RACE_TIME_TRIAL,
    league="ASOCIACIÓN DE REMO DEL CANTÁBRICO 2",
    town="COLINDRES",
    organizer=None,
    sponsor=None,
    normalized_names=[("BANDERA RIA DEL ASON", 17)],
    race_ids=["1234"],
    url=None,
    datasource=Datasource.ARC.value,
    gender=GENDER_MALE,
    category=CATEGORY_ABSOLUT,
    participants=[],
    race_laps=4,
    race_lanes=7,
    cancelled=False,
)

_PARTICIPANTS = [
    Participant(
        gender=GENDER_MALE,
        category=CATEGORY_ABSOLUT,
        club_name="RASPAS A.E.",
        lane=1,
        series=1,
        laps=["06:08.000000", "11:12.000000", "17:44.000000", "22:43.450000"],
        distance=5556,
        handicap=None,
        participant="RASPAS",
        race=_RACE,
        absent=False,
        retired=False,
        guest=False,
    ),
    Participant(
        gender=GENDER_MALE,
        category=CATEGORY_ABSOLUT,
        club_name="NATURHOUSE - MUNDAKA",
        lane=1,
        series=2,
        laps=["05:29.000000", "10:29.000000", "16:16.000000", "21:13.900000"],
        distance=5556,
        handicap=None,
        participant="MUNDAKA",
        race=_RACE,
        absent=False,
        retired=False,
        guest=False,
    ),
]

_RACE_NAMES = [
    RaceName(
        race_id="446",
        name="KEPA DEUN ARRANTZALEEN KOFRADIA XXII. IKURRIÑA",
    ),
    RaceName(race_id="474", name="PLAY OFF I"),
    RaceName(race_id="475", name="PLAY OFF II"),
]
