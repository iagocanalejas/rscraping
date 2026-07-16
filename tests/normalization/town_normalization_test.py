import pytest

from rscraping.data.normalization import normalize_town


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
