import unittest

from rscraping.data.normalization.clubs import normalize_club_name


class TestClubNameNormalization(unittest.TestCase):
    def setUp(self) -> None:
        self.NAMES = [
            "C.R. CABO DA CRUZ - C.R. PUEBLA",
            "CCD CESANTES - RODAVIGO",
        ]

    def test_club_name_normalization(self):
        results = [
            "PUEBLA - CABO",
            "CESANTES",
        ]

        for idx, club_name in enumerate(self.NAMES):
            self.assertEqual(normalize_club_name(club_name), results[idx])
