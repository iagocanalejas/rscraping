import unittest

from rscraping.data.normalization import normalize_town


class TestTownNormalization(unittest.TestCase):
    def test_town_normalization(self) -> None:
        results = [
            ("PORTO DA POBRA", "A POBRA DO CARAMIÑAL"),
            ("PUERTO DE TIRÁN", "TIRÁN"),
            ("BAHÍA DE SANTANDER", "SANTANDER"),
            ("PLAYA DE LA CONCHA", "LA CONCHA"),
            ("  POBRA   - A CORUÑA  ", "A POBRA DO CARAMIÑAL"),
        ]

        for name, normalized in results:
            self.assertEqual(normalize_town(name), normalized)
