import os
import unittest

from parsel.selector import Selector

from rscraping.data.constants import CATEGORY_ABSOLUT, GENDER_MALE, RACE_TIME_TRIAL, RACE_TRAINERA
from rscraping.data.models import Datasource, Lineup, Participant, Race, RaceName
from rscraping.parsers.html.arc import ARCHtmlParser


class TestARCParser(unittest.TestCase):
    def setUp(self):
        self.parser = ARCHtmlParser()
        self.fixtures = os.path.join(os.getcwd(), "fixtures", "html")

    def test_parse_race(self):
        with open(os.path.join(self.fixtures, "arc_details.html")) as file:
            race = self.parser.parse_race(
                Selector(file.read()),
                race_id="1234",
                is_female=False,
            )
        if not race:
            raise ValueError("unable to parse race")

        participants = race.participants
        race.participants = []

        self.assertEqual(race, self._RACE)
        self.assertEqual(participants, self._PARTICIPANTS)

    def test_parse_race_ids(self):
        with open(os.path.join(self.fixtures, "arc_races.html")) as file:
            ids = self.parser.parse_race_ids(Selector(file.read()))

        self.assertEqual(list(ids), ["446", "474", "475"])

    def test_parse_race_names(self):
        with open(os.path.join(self.fixtures, "arc_races.html")) as file:
            race_names = self.parser.parse_race_names(Selector(file.read()), is_female=False)

        self.assertEqual(list(race_names), self._RACE_NAMES)

    def test_parse_club_ids(self):
        with open(os.path.join(self.fixtures, "arc_lineups.html")) as file:
            ids = self.parser.parse_club_ids(Selector(file.read()))

        self.assertEqual(list(ids), ["481", "485"])

    def test_parse_lineup(self):
        with open(os.path.join(self.fixtures, "arc_lineup.html")) as file:
            lineup = self.parser.parse_lineup(Selector(file.read()))

        self.assertEqual(lineup, self._LINEUP)

    _RACE = Race(
        name="XVII BANDERA RIA DEL ASON",
        date="22/08/2009",
        day=1,
        modality=RACE_TRAINERA,
        type=RACE_TIME_TRIAL,
        league="ASOCIACIÓN DE REMO DEL CANTÁBRICO 2",
        town="COLINDRES",
        organizer=None,
        sponsor=None,
        normalized_names=[("BANDERA RIA DEL ASON", 17)],
        race_ids=["1234"],
        url=None,
        gender=GENDER_MALE,
        datasource=Datasource.ARC.value,
        participants=[],
        race_laps=4,
        race_lanes=7,
        cancelled=False,
    )
    _PARTICIPANTS = [
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="RASPAS A.E.",
            lane=1,
            series=1,
            laps=["06:08.000000", "11:12.000000", "17:44.000000", "22:43.450000"],
            distance=5556,
            handicap=None,
            participant="RASPAS",
            race=_RACE,
            disqualified=False,
        ),
        Participant(
            gender=GENDER_MALE,
            category=CATEGORY_ABSOLUT,
            club_name="NATURHOUSE - MUNDAKA",
            lane=1,
            series=2,
            laps=["05:29.000000", "10:29.000000", "16:16.000000", "21:13.900000"],
            distance=5556,
            handicap=None,
            participant="MUNDAKA",
            race=_RACE,
            disqualified=False,
        ),
    ]
    _RACE_NAMES = [
        RaceName(
            race_id="446",
            name="KEPA DEUN ARRANTZALEEN KOFRADIA XXII. IKURRIÑA",
        ),
        RaceName(race_id="474", name="PLAY OFF I"),
        RaceName(race_id="475", name="PLAY OFF II"),
    ]
    _LINEUP = Lineup(
        race="XXIX BANDERA REAL ASTILLERO DE GUARNIZO",
        club="ORIO",
        coach="ANGEL MARIA LARRAÑAGA ARTOLA",
        delegate="LINO Mª CARRERA SOLABARRIETA",
        coxswain="JON BARRANCO ALBENIZ",
        starboard=[
            "EKHI GOZATEGI URBIETA",
            "ADUR TAPIA ITURZAETA",
            "IMANOL SARASOLA ERASUN",
            "JOKIN AZKONOBIETA UGARTEMENDIA",
            "IKER ZINKUNEGI URBIETA",
            "OIHAN MANTEROLA KAMIO",
        ],
        larboard=[
            "GORKA TOLEDO PELLEJERO",
            "OIHAN GOZATEGI URBIETA",
            "JOSEBA PAGADIZABAL IRIZAR",
            "YANNIK BRIONES DUARTE",
            "IBAI LIZARRALDE ARANALDE",
            "JON AZPIROZ ANZA",
        ],
        substitute=[
            "MARKEL BERISTAIN ALKORTA",
            "MATTIN BEREZIARTUA OÑEDERRA",
            "UNAI OTAEGUI AYERZA",
            "JON OLAIZOLA MARTINEZ",
        ],
        bow="UNAX LARRAÑAGA ANDUEZA",
        images=[],
    )
