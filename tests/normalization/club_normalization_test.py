import unittest

from rscraping.data.normalization import normalize_club_name


class TestClubNormalization(unittest.TestCase):
    def setUp(self) -> None:
        self.NAMES = [
            "C.R. CABO DA CRUZ - C.R. PUEBLA",
            "C.R. CABO DA CRUZ",
            "CCD CESANTES - RODAVIGO",
            "C.R. CABANA FERROL B",
            "C.R. PUEBLA B",
            "C.R.O. ARRAUN LAGUNAK",
            "C.R. DEL NALÓN",
            "DONOSTIA ARRAUN LAGUNAK",
            "E.D. MOAÑA",
            "DEUSTO A.T. - C.R. SAN NICOLÁS A.T. B",
            "UROLA KOSTA A.E.",
            "C.R. IBERIA B",
            "C.M. CASTROPOL",
            "KAIKU A.E. - C.R. IBERIA",
            "KOXTAPE - DENIA",
        ]

    def test_club_name_normalization(self) -> None:
        results = [
            "PUEBLA - CABO",
            "CABO DA CRUZ",
            "CESANTES",
            "A CABANA B",
            "PUEBLA B",
            "ARRAUN LAGUNAK",
            "NALÓN",
            "DONOSTIA ARRAUN LAGUNAK",
            "MOAÑA",
            "DEUSTO - SAN NICOLÁS B",
            "UROLA KOSTA",
            "IBERIA B",
            "CASTROPOL",
            "KAIKU - IBERIA",
            "KOXTAPE - DENIA",
        ]

        for idx, club_name in enumerate(self.NAMES):
            self.assertEqual(normalize_club_name(club_name), results[idx])
