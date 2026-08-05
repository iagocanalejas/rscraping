from datetime import datetime

import pytest

from rscraping.data.constants import LAP_FORMAT
from rscraping.data.normalization import normalize_lap_time, normalize_spanish_months


@pytest.mark.parametrize(
    ("lap_time, expected"),
    (
        (":18,62", "00:18.62"),
        (":45", "00:45.00"),
        ("2102:48", "21:02.48"),
        ("25:2257", "25:22.57"),
        ("028:24", "28:24.00"),
        ("00:009", None),
        ("21.13.66", "21:13.66"),
        ("11,10", "11:10.00"),
    ),
)
def test_lap_time_normalization(lap_time, expected) -> None:
    result = datetime.strptime(expected, LAP_FORMAT).time() if expected else None
    assert normalize_lap_time(lap_time) == result


@pytest.mark.parametrize(
    ("phrase, expected"),
    [
        ("REGATA EN XANEIRO", "REGATA EN ENERO"),
        ("CARRERA EN FEBREIRO", "CARRERA EN FEBRERO"),
        ("EVENTO EN MAIO", "EVENTO EN MAYO"),
        ("CARRERA EN XUÑO", "CARRERA EN JUNIO"),
    ],
)
def test_normalize_spanish_months(phrase, expected) -> None:
    assert normalize_spanish_months(phrase) == expected
