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


def test_find_league() -> None:
    assert find_league("LGT PLAY OFF") == "LGT"
    assert find_league("ARC PLAY OFF") == "ARC"
    assert find_league("ACT PLAY OFF") == "ACT"
    assert find_league("LGT AND ARC PLAY OFF") == "ACT"
    assert find_league("LGT A") == "LIGA GALEGA DE TRAIÑAS A"
    assert find_league("LGT B") == "LIGA GALEGA DE TRAIÑAS B"
    assert find_league("LGT F") == "LIGA GALEGA DE TRAIÑAS FEMENINA"
    assert find_league("EUSKO LABEL LIGA") == "EUSKO LABEL LIGA"
    assert find_league("EUSKOTREN LIGA") == "LIGA EUSKOTREN"
    assert find_league("ARC") == "ASOCIACIÓN DE REMO DEL CANTÁBRICO 1"
    assert find_league("ARC2") == "ASOCIACIÓN DE REMO DEL CANTÁBRICO 2"
    assert find_league("ETE COMPETITION") == "EMAKUMEZKO TRAINERUEN ELKARTEA"
