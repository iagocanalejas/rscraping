import unittest

from rscraping.data.normalization import find_league, normalize_league_name


class TestLeagueNormalization(unittest.TestCase):
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

    def test_find_league(self):
        self.assertEqual(find_league("LGT PLAY OFF"), "LGT")
        self.assertEqual(find_league("ARC PLAY OFF"), "ARC")
        self.assertEqual(find_league("ACT PLAY OFF"), "ACT")
        self.assertEqual(find_league("LGT AND ARC PLAY OFF"), "ACT")
        self.assertEqual(find_league("LGT A"), "LIGA A")
        self.assertEqual(find_league("LGT B"), "LIGA B")
        self.assertEqual(find_league("LGT F"), "LIGA FEM")
        self.assertEqual(find_league("EUSKO LABEL LIGA"), "EUSKO LABEL LIGA")
        self.assertEqual(find_league("EUSKOTREN LIGA"), "LIGA EUSKOTREN")
        self.assertEqual(find_league("ARC"), "ASOCIACIÓN DE REMO DEL CANTÁBRICO 1")
        self.assertEqual(find_league("ARC2"), "ASOCIACIÓN DE REMO DEL CANTÁBRICO 2")
        self.assertEqual(find_league("ETE COMPETITION"), "EMAKUMEZKO TRAINERUEN ELKARTEA")
