import unittest

from rscraping.data.normalization.races import normalize_name_parts, normalize_race_name


class TestRaceNameNormalization(unittest.TestCase):
    def setUp(self) -> None:
        self.NAMES = [
            "XXXVIII. El Correo Ikurriña - Kutxabank SN - Lekeitioko Udala",
            "Hondarribiko XXXVI. Bandera / Mapfre Sari Nagusia",
            "Orioko XXXIII. Estropada - Orio Kanpina XI. Bandera",
            "Getxoko Estropaden XLV. Ikurriña - J.A. Agirre Lehendakariaren XIX. Omenaldia",
        ]

    def test_race_name_normalization(self):
        results = [
            "XXXVIII EL CORREO IKURRIÑA - KUTXABANK SARI NAGUSIA - LEKEITIOKO UDALA",
            "HONDARRIBIKO XXXVI BANDERA - MAPFRE SARI NAGUSIA",
            "ORIOKO XXXIII ESTROPADA - ORIO KANPINA XI BANDERA",
            "GETXOKO ESTROPADEN XLV IKURRIÑA - JOSE ANTONIO AGIRRE LEHENDAKARIAREN XIX OMENALDIA",
        ]

        for idx, race_name in enumerate(self.NAMES):
            self.assertEqual(normalize_race_name(race_name), results[idx])

    def test_normalize_name_parts(self):
        results = [
            [("EL CORREO IKURRIÑA", 38), ("KUTXABANK SARI NAGUSIA", None), ("LEKEITIOKO UDALA", None)],
            [("HONDARRIBIKO BANDERA", 36), ("MAPFRE SARI NAGUSIA", None)],
            [("ORIOKO ESTROPADA", 33), ("ORIO KANPINA BANDERA", 11)],
            [("GETXOKO ESTROPADEN IKURRIÑA", 45), ("JOSE ANTONIO AGIRRE LEHENDAKARIAREN OMENALDIA", 19)],
        ]

        races = [normalize_race_name(n) for n in self.NAMES]
        for idx, race_name in enumerate(races):
            self.assertEqual(normalize_name_parts(race_name), results[idx])
