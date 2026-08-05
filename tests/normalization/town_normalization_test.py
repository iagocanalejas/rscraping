import pytest

from rscraping.data.normalization import normalize_town, remove_province
from rscraping.data.normalization.towns import extract_town


@pytest.mark.parametrize(
    ("name, normalized"),
    (
        ("PORTO DA POBRA", "A POBRA DO CARAMIÑAL"),
        ("PUERTO DE TIRÁN", "TIRÁN"),
        ("BAHÍA DE SANTANDER", "SANTANDER"),
        ("PLAYA DE LA CONCHA", "LA CONCHA"),
        ("  POBRA   - A CORUÑA  ", "A POBRA DO CARAMIÑAL"),
    ),
)
def test_town_normalization(name, normalized) -> None:
    assert normalize_town(name) == normalized


@pytest.mark.parametrize(
    ("town, expected"),
    [
        ("ZIERBENA BIZKAIA", "ZIERBENA"),
        ("CASTROPOL PONTEVEDRA", "CASTROPOL"),
        ("SANTANDER CANTABRIA", "SANTANDER"),
        ("LUGO GIPUZKOA", "GIPUZKOA"),
        ("NO PROVINCE", "NO PROVINCE"),
    ],
)
def test_remove_province(town, expected) -> None:
    assert remove_province(town) == expected


@pytest.mark.parametrize(
    ("name, expected"),
    [
        ("BANDEIRA CONCELLO DE BUEU (ZIERBENA)", "ZIERBENA"),
        ("CAMPEONATO CLASIFICATORIA (CLASIFICATORIA)", None),
        ("BANDEIRA NORMAL", None),
    ],
)
def test_extract_town(name, expected) -> None:
    assert extract_town(name) == expected
