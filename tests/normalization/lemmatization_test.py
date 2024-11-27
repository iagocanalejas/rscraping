import unittest

from rscraping.data.normalization import lemmatize


class TestLemmatization(unittest.TestCase):
    def test_lemmatization(self):
        results = [
            ("BANDEIRA CONCELLO DE BUEU", ["bandera", "ayuntamiento", "bueu"]),
            ("EL CORREO IKURRIÑA", ["correo", "bandera"]),
            ("BERMEO HIRIKO BANDERA", ["bermeo", "ayuntamiento", "bandera"]),
        ]

        for name, lemmas in results:
            self.assertEqual(set(lemmatize(name)), set(lemmas))
