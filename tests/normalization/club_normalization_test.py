import pytest

from rscraping.data.normalization import normalize_club_name


@pytest.mark.parametrize(
    ("name, expected"),
    [
        ("C.R. CABO DA CRUZ - C.R. PUEBLA", "PUEBLA - CABO"),
        ("C.R. CABO DA CRUZ", "CABO DA CRUZ"),
        ("CCD CESANTES - RODAVIGO", "CESANTES"),
        ("C.R. CABANA FERROL B", "A CABANA B"),
        ("C.R. PUEBLA B", "PUEBLA B"),
        ("C.R.O. ARRAUN LAGUNAK", "ARRAUN LAGUNAK"),
        ("C.R. DEL NALÓN", "NALÓN"),
        ("DONOSTIA ARRAUN LAGUNAK", "DONOSTIA ARRAUN LAGUNAK"),
        ("E.D. MOAÑA", "MOAÑA"),
        ("DEUSTO A.T. - C.R. SAN NICOLÁS A.T. B", "DEUSTO - SAN NICOLÁS B"),
        ("UROLA KOSTA A.E.", "UROLA KOSTA"),
        ("C.R. IBERIA B", "IBERIA B"),
        ("C.M. CASTROPOL", "CASTROPOL"),
        ("KAIKU A.E. - C.R. IBERIA", "KAIKU - IBERIA"),
        ("KOXTAPE - DENIA", "KOXTAPE - DENIA"),
    ],
)
def test_club_name_normalization(name, expected) -> None:
    assert normalize_club_name(name) == expected
