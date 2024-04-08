import os
import unittest

import fitz

from rscraping.data.models import Lineup
from rscraping.parsers.pdf.lgt import LGTPdfParser


class TestLGTParser(unittest.TestCase):
    def setUp(self):
        self.parser = LGTPdfParser()
        self.fixtures = os.path.join(os.getcwd(), "tests", "fixtures", "pdf")

    def test_parse_race(self):
        lineup = None
        with fitz.open(os.path.join(self.fixtures, "lgt_lineup.pdf")) as pdf:
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                lineup = self.parser.parse_lineup(page)

        if not lineup:
            raise ValueError("unable to parse lineup")
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
        images=[],
    )
