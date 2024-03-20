import unittest

from rscraping.data.normalization import normalize_league_name


class TestLeagueNameNormalization(unittest.TestCase):
    def setUp(self) -> None:
        self.NAMES = [
            "LIGA FEM",
        ]

    def test_league_name_normalization(self):
        results = [
            "LIGA GALEGA DE TRAIÑAS FEMENINA",
        ]

        for idx, league_name in enumerate(self.NAMES):
            self.assertEqual(normalize_league_name(league_name), results[idx])
