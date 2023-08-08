import os
import unittest

from pypdf import PdfReader

from rscraping.data.models import Lineup
from rscraping.parsers.pdf.lgt import LGTPdfParser


class TestLGTParser(unittest.TestCase):
    def setUp(self):
        self.parser = LGTPdfParser()
        self.fixtures = os.path.join(os.getcwd(), "fixtures", "pdf")

    def test_parse_race(self):
        with open(os.path.join(self.fixtures, "lgt_lineup.pdf"), "rb") as file:
            page = PdfReader(file).pages[0]
            lineup = self.parser.parse_lineup(page)

        self.assertEqual(lineup, self._LINEUP)

    _LINEUP = Lineup(
        race="XVIII BANDEIRA CONCELLO DE A POBRA",
        club="PUEBLA",
        coach="MANUEL RAUL PAZOS PARDAVILA",
        delegate="EMILIO JOSE DIESTE REGADES",
        coxswain="RUBEN GONZALEZ PARGA",
        starboard=[
            "UNAY VAZQUEZ RIVAS",
            "SERGIO TUBIO DAVILA",
            "IAGO SANTOS DOMINGUEZ",
            "CESAR GONZALEZ FERNANDEZ",
            "FRANCISCO DIAZ FERNANDEZ",
            "MIGUEL TUBIO TARRIO",
        ],
        larboard=[
            "DAVID VIDAL PLACES",
            "ADRIAN GONZALEZ LOPEZ",
            "JOSE JAVIER GARCIA OUVIÑA",
            "JUAN ANTONIO MILLAN FIGUEIRIDO",
            "LUCAS LIJO TRIÑANES",
            "IVAN LODEIRO ALCALDE",
        ],
        substitute=["JACOBO PAZOS PARDAVILA", "MARTIN GONZALEZ LOPEZ"],
        bow="RUBEN OLIVEIRA PIÑEIRO",
    )
