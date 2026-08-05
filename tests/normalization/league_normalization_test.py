import pytest

from rscraping.data.normalization import find_league, normalize_league_name


@pytest.mark.parametrize(
    ("name, expected"),
    [
        ("LIGA FEM", "LIGA GALEGA DE TRAIÑAS FEMENINA"),
    ],
)
def test_league_name_normalization(name, expected) -> None:
    assert normalize_league_name(name) == expected


@pytest.mark.parametrize(
    ("text", "league"),
    [
        ("LGT PLAY OFF", "LGT"),
        ("ARC PLAY OFF", "ARC"),
        ("ACT PLAY OFF", "ACT"),
        ("LGT AND ARC PLAY OFF", "ACT"),
        ("LGT A", "LIGA GALEGA DE TRAIÑAS A"),
        ("LGT B", "LIGA GALEGA DE TRAIÑAS B"),
        ("LGT F", "LIGA GALEGA DE TRAIÑAS FEMENINA"),
        ("EUSKO LABEL LIGA", "EUSKO LABEL LIGA"),
        ("EUSKOTREN LIGA", "LIGA EUSKOTREN"),
        ("ARC", "ASOCIACIÓN DE REMO DEL CANTÁBRICO 1"),
        ("ARC2", "ASOCIACIÓN DE REMO DEL CANTÁBRICO 2"),
        ("ETE COMPETITION", "EMAKUMEZKO TRAINERUEN ELKARTEA"),
    ],
)
def test_find_league(text, league) -> None:
    assert find_league(text) == league
