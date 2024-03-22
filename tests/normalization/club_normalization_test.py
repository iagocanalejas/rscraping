import unittest

from rscraping.data.normalization.clubs import normalize_club_name


class TestClubNormalization(unittest.TestCase):
    def setUp(self) -> None:
        self.NAMES = [
            "C.R. CABO DA CRUZ - C.R. PUEBLA",
            "CCD CESANTES - RODAVIGO",
            "C.R. CABANA FERROL B",
            "C.R. PUEBLA B",
        ]

    def test_club_name_normalization(self):
        results = [
            "PUEBLA - CABO",
            "CESANTES",
            "A CABANA B",
            "PUEBLA B",
        ]

        for idx, club_name in enumerate(self.NAMES):
            self.assertEqual(normalize_club_name(club_name), results[idx])
