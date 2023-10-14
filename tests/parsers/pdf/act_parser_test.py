import os
import unittest

import fitz

from rscraping.data.models import Lineup
from rscraping.parsers.pdf.act import ACTPdfParser


class TestACTParser(unittest.TestCase):
    def setUp(self):
        self.parser = ACTPdfParser()
        self.fixtures = os.path.join(os.getcwd(), "fixtures", "pdf")

    def test_parse_race(self):
        with fitz.open(os.path.join(self.fixtures, "act_lineup.pdf")) as pdf:
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                lineup = self.parser.parse_lineup(page)

        self.assertEqual(lineup, self._LINEUP)

    _LINEUP = Lineup(
        race="XL BANDERA PETRONOR",
        club="ONDARROA",
        coach="IÑAKI ERRASTI",
        delegate="HASIER ETXABURU",
        coxswain="IÑIGO LARRINAGA",
        starboard=[
            "JOSEBA ARISTI",
            "JON ARRIOLA",
            "JON CARRILLO",
            "IGOR GURUCHARRI",
            "ANDER LARRAÑAGA",
            "IKER MURGIONDO",
        ],
        larboard=["IKER INCHAURTIETA", "BEÑAT EIZAGIRRE", "ANDONI LOPEZ", "ASIER IRUETA", "IVAN LOPEZ", "JOSU ELU"],
        substitute=[
            "EKAITZ BADIOLA",
            "UNAX BEDIALAUNETA",
            "UGAITZ ELU",
            "IÑAKI ERRASTI",
            "XANET GIMENO",
            "MARKEL KALZAKORTA",
        ],
        bow="JULEN AROSTEGI",
        images=[],
    )
