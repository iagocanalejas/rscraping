import pytest

from rscraping.data.normalization import lemmatize


@pytest.mark.parametrize(
    ("name, lemmas"),
    [
        ("BANDEIRA CONCELLO DE BUEU", ["bandera", "ayuntamiento", "bueu"]),
        ("EL CORREO IKURRIÑA", ["correo", "bandera"]),
        ("BERMEO HIRIKO BANDERA", ["bermeo", "ayuntamiento", "bandera"]),
    ],
)
def test_lemmatization(name, lemmas) -> None:
    assert set(lemmatize(name)) == set(lemmas)
