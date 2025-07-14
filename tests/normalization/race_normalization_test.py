import unittest

from rscraping.data.normalization import normalize_name_parts, normalize_race_name, remove_day_indicator


class TestRaceNormalization(unittest.TestCase):
    def setUp(self) -> None:
        self.NAMES = [
            "XXXVIII. El Correo Ikurriña - Kutxabank SN - Lekeitioko Udala",
            "Hondarribiko XXXVI. Bandera / Mapfre Sari Nagusia",
            "Orioko XXXIII. Estropada - Orio Kanpina XI. Bandera",
            "Getxoko Estropaden XLV. Ikurriña - J.A. Agirre Lehendakariaren XIX. Omenaldia",
            "XVII BANDEIRA CIDADE DE FERROL III MEMORIAL MIGUEL DERUNGS CRIADO",
            "X BANDERA ILLA DO SAMERTOLAMEU-FANDICOSTA",
            "CAMPEONATO DE GUIPÚZCOA",
            "BANDERA CONCELLO DE BUEU (ACT)",
            "ASOCIACIÓN DE REMO DEL CANTÁBRICO 2:BANDERA VILLA DE LAREDO",
            "REGATA LIGA GALEGA DE TRAINERAS A",
        ]

    def test_race_name_normalization(self):
        results = [
            "XXXVIII EL CORREO IKURRIÑA - KUTXABANK SARI NAGUSIA - LEKEITIOKO UDALA",
            "HONDARRIBIKO XXXVI BANDERA - MAPFRE SARI NAGUSIA",
            "ORIOKO XXXIII ESTROPADA - ORIO KANPINA XI BANDERA",
            "GETXOKO ESTROPADEN XLV IKURRIÑA - JOSE ANTONIO AGIRRE LEHENDAKARIAREN XIX OMENALDIA",
            "XVII BANDEIRA CIDADE DE FERROL III MEMORIAL MIGUEL DERUNGS CRIADO",
            "X BANDEIRA ILLA DO SAMERTOLAMEU - FANDICOSTA",
            "CAMPEONATO DE GIPÚZKOA",
            "BANDERA CONCELLO DE BUEU",
            "BANDERA VILLA DE LAREDO",
            "REGATA LIGA GALEGA DE TRAINERAS A",
        ]

        for idx, race_name in enumerate(self.NAMES):
            self.assertEqual(normalize_race_name(race_name), results[idx])

    def test_name_parts_normalization(self):
        results = [
            [("EL CORREO IKURRIÑA", 38), ("KUTXABANK SARI NAGUSIA", None), ("LEKEITIOKO UDALA", None)],
            [("HONDARRIBIKO BANDERA", 36), ("MAPFRE SARI NAGUSIA", None)],
            [("ORIOKO ESTROPADA", 33), ("ORIO KANPINA BANDERA", 11)],
            [("GETXOKO ESTROPADEN IKURRIÑA", 45), ("JOSE ANTONIO AGIRRE LEHENDAKARIAREN OMENALDIA", 19)],
            [("BANDEIRA CIDADE DE FERROL", 17), ("MEMORIAL MIGUEL DERUNGS CRIADO", 3)],
            [("BANDEIRA ILLA DO SAMERTOLAMEU - FANDICOSTA", 10)],
            [("CAMPEONATO DE GIPÚZKOA", None)],
            [("BANDERA CONCELLO DE BUEU", None)],
            [("BANDERA VILLA DE LAREDO", None)],
            [("REGATA LIGA GALEGA DE TRAINERAS A", None)],
        ]

        races = [normalize_race_name(n) for n in self.NAMES]
        for idx, race_name in enumerate(races):
            self.assertEqual(normalize_name_parts(race_name), results[idx])

    def test_day_indicator_normalization(self):
        pairs = [("PLAY-OFF LGT XORNADA 2 (ARES)", "PLAY-OFF LGT (ARES)")]

        for name, normalized in pairs:
            self.assertEqual(remove_day_indicator(name), normalized)
