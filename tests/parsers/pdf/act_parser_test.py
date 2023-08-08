import os
import unittest

from pypdf import PdfReader

from rscraping.data.models import Lineup
from rscraping.parsers.pdf.act import ACTPdfParser


class TestACTParser(unittest.TestCase):
    def setUp(self):
        self.parser = ACTPdfParser()
        self.fixtures = os.path.join(os.getcwd(), "fixtures", "pdf")

    def test_parse_race(self):
        with open(os.path.join(self.fixtures, "act_lineup.pdf"), "rb") as file:
            page = PdfReader(file).pages[0]
            lineup = self.parser.parse_lineup(page)

        self.assertEqual(lineup, self._LINEUP)

    _LINEUP = Lineup(
        race="XL BANDERA PETRONOR",
        club="ONDARROA",
        coach="IÑAKI ERRASTI",
        delegate="HASIER ETXABURU",
        coxswain=None,
        starboard=[
            "JOSEBA ARISTI",
            "JULEN AROSTEGI",
            "JON ARRIOLA",
            "JON CARRILLO",
            "BEÑAT EIZAGIRRE",
            "JOSU ELU",
            "IGOR GURUCHARRI",
            "IKER INCHAURTIETA",
            "ASIER IRUETA",
            "ANDER LARRAÑAGA",
            "IÑIGO LARRINAGA",
            "ANDONI LOPEZ",
            "IVAN LOPEZ",
            "IKER MURGIONDO",
        ],
        larboard=[
            "JOSEBA ARISTI",
            "JULEN AROSTEGI",
            "JON ARRIOLA",
            "JON CARRILLO",
            "BEÑAT EIZAGIRRE",
            "JOSU ELU",
            "IGOR GURUCHARRI",
            "IKER INCHAURTIETA",
            "ASIER IRUETA",
            "ANDER LARRAÑAGA",
            "IÑIGO LARRINAGA",
            "ANDONI LOPEZ",
            "IVAN LOPEZ",
            "IKER MURGIONDO",
        ],
        substitute=[
            "EKAITZ BADIOLA",
            "UNAX BEDIALAUNETA",
            "UGAITZ ELU",
            "IÑAKI ERRASTI",
            "XANET GIMENO",
            "MARKEL KALZAKORTA",
        ],
        bow=None,
    )
