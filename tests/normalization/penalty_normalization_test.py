import unittest

from rscraping.data.constants import (
    BOAT_WEIGHT_LIMIT,
    COLLISION,
    LACK_OF_COMPETITIVENESS,
    NULL_START,
    OFF_THE_FIELD,
    SINKING,
    STARBOARD_TACK,
    WRONG_LINEUP,
)
from rscraping.data.models import Penalty
from rscraping.data.normalization.penalty import is_cancelled, normalize_penalty


class TestPenaltyNormalization(unittest.TestCase):
    def test_time_note_normalization(self):
        notes = [
            "El tiempo de Rianxo había sido de 19:39.13.",
            "El tiempo de Tirán había sido de 19:23.52, el de Mecos de 19:31.32 y el de Cabo da Cruz de 19:13.70.",
            "El tiempo de Coruxo había sido de 22:32.16. El tiempo de Puebla había sido de 22:16.98.",
            "Donostia Arraun Lagunak fue descalificado, su tiempo había sido de 20:58.16.",
            "Hondarribia había realizado un tiempo de 20:29.1.",
            "El tiempo de Portugalete había sido de 21:29.20, el de Santurtzi de 21:15.50, el de Trinxerpe de 20:35.00 y el de Zarautz de 20:57.70.",  # noqa: E501
        ]
        results = [
            {
                "RIANXO": ("19:39.130000", None),
            },
            {
                "TIRÁN": ("19:23.520000", None),
                "MECOS": ("19:31.320000", None),
                "CABO DA CRUZ": ("19:13.700000", None),
            },
            {
                "CORUXO": ("22:32.160000", None),
                "PUEBLA": ("22:16.980000", None),
            },
            {
                "DONOSTIA ARRAUN LAGUNAK": ("20:58.160000", None),
            },
            {
                "HONDARRIBIA": ("20:29.100000", None),
            },
            {
                "PORTUGALETE": ("21:29.200000", None),
                "SANTURTZI": ("21:15.500000", None),
                "TRINXERPE": ("20:35.000000", None),
                "ZARAUTZ": ("20:57.700000", None),
            },
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text), results[idx])

    def test_starboard_tack_normalization(self):
        notes = [
            "Vila de Cangas realizó la primera ciaboga por estribor.",
            "Ría de Marín realizó una ciaboga por estribor.",
            "Fortuna realizió una ciaboga por estribor",
            "Castro había dado la tercera ciaboga por estribor, siendo su tiempo de 21:48.3",
            "Castro ocupó la séptima posición pero fue descalificado por realizar la segunda ciaboga por estribor. Su tiempo había sido de 21:48.12.",  # noqa: E501
            "Castro fue descalificado por tomar la segunda ciaboga por estribor y no rectificar.",
        ]
        results = [
            {
                "VILA DE CANGAS": (None, Penalty(disqualification=True, reason=STARBOARD_TACK)),
            },
            {
                "RÍA DE MARÍN": (None, Penalty(disqualification=True, reason=STARBOARD_TACK)),
            },
            {
                "FORTUNA": (None, Penalty(disqualification=True, reason=STARBOARD_TACK)),
            },
            {
                "CASTRO": ("21:48.300000", Penalty(disqualification=True, reason=STARBOARD_TACK)),
            },
            {
                "CASTRO": ("21:48.120000", Penalty(disqualification=True, reason=STARBOARD_TACK)),
            },
            {
                "CASTRO": (None, Penalty(disqualification=True, reason=STARBOARD_TACK)),
            },
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text), results[idx])

    def test_off_the_field_normalization(self):
        notes = [
            "San Simón fue descalificado por dejar por estribor una baliza del recorrido y la meta.",
            "San Simón y A Cabana pasaron la baliza de meta por estribor. El tiempo de San Simón había sido de 24:34.29 y el de A Cabana de 24:30.41.",  # noqa: E501
            "Cesantes y el Náutico de Vigo dejaron la baliza de meta por estribor. El tiempo de Cesantes había sido de 21:52.58 y el del Náutico de Vigo de 21:39.47.",  # noqa: E501
            "Castropol entró a meta fuera de línea (la línea de meta entre la baliza uno y la cinco). Su tiempo había sido de 24:52.57.",  # noqa: E501
            "Tirán fue descalificada por entrar en meta dejando la boya por estribor. Su tiempo había sido de 21:58.00.",  # noqa: E501
            "El tiempo de Tirán había sido 19:15.32, pero fue descalificado por dejar su baliza por estribor a la entrada a meta.",  # noqa: E501
        ]
        results = [
            {
                "SAN SIMÓN": (None, Penalty(disqualification=True, reason=OFF_THE_FIELD)),
            },
            {
                "SAN SIMÓN": ("24:34.290000", Penalty(disqualification=True, reason=OFF_THE_FIELD)),
                "CABANA": ("24:30.410000", Penalty(disqualification=True, reason=OFF_THE_FIELD)),
            },
            {
                "CESANTES": ("21:52.580000", Penalty(disqualification=True, reason=OFF_THE_FIELD)),
                "NÁUTICO DE VIGO": ("21:39.470000", Penalty(disqualification=True, reason=OFF_THE_FIELD)),
            },
            {
                "CASTROPOL": ("24:52.570000", Penalty(disqualification=True, reason=OFF_THE_FIELD)),
            },
            {
                "TIRÁN": ("21:58.000000", Penalty(disqualification=True, reason=OFF_THE_FIELD)),
            },
            {
                "TIRÁN": ("19:15.320000", Penalty(disqualification=True, reason=OFF_THE_FIELD)),
            },
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text), results[idx])

    def test_lack_of_competitiveness_normalization(self):
        notes = [
            "Se consideró que a Ondarroa le faltó voluntad de competir, infringiendo el artículo 39 del vigente Código de Regatas, que obliga a toda tripulación que tome la salida a remar a ritmo de regata hasta terminar.",  # noqa: E501
        ]
        results = [
            {
                "ONDARROA": (None, Penalty(disqualification=True, reason=LACK_OF_COMPETITIVENESS)),
            }
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text), results[idx])

    def test_null_start_normalization(self):
        notes = [
            "Virxe da Guía tuvo dos salidas nulas.",
            "Tirán compitió fuera de regata por salidas nulas. Su tiempo había sido de 20:55.",
            "Fortuna quedó fuera de regata en la primera jornada por llegar tarde a la salida.",
        ]
        results = [
            {
                "VIRXE DA GUÍA": (None, Penalty(disqualification=True, reason=NULL_START)),
            },
            {
                "TIRÁN": ("20:55.000000", Penalty(disqualification=True, reason=NULL_START)),
            },
            {
                "FORTUNA": (None, Penalty(disqualification=True, reason=NULL_START)),
            },
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text), results[idx])

    def test_collision_normalization(self):
        notes = [
            "Rianxo salió demasiado abierto.",
            "Cabo da Cruz se puso delante de Chapela en la meta. Su tiempo había sido de 21:25.13.",
            "Samertolameu fue descalificado por ponerse delante de Cesantes. Su tiempo había sido de 20:17.82.",
            "Samertolameu estorbó a Bueu en la tercera virada. Su tiempo había sido el mejor con 19:07.89.",
            "Cabo da Cruz y Mecos no disputaban la Bandera sino la clasificatoria. Puebla salió muy abierta en la segunda ciaboga, lo que molestó a Chapela. Su tiempo había sido de 21:25.02.",  # noqa: E501
            "El tiempo de Amegrove había sido de 20:09.33, pero fue descalificada por invasión de la calle del Náutico de Vigo a la salida de la segunda ciaboga.",  # noqa: E501
            "En la segunda jornada Donibaneko fue descalificado por invadir la calle de Santurtzi en la segunda ciaboga. Terminó con un tiempo de 20:59,35.",  # noqa: E501
            "Trintxerpe se chocó contra una roca.",
            "En la primera jornada, Santander había llegado junto a Astillero en el segundo puesto de tanda, pero abordó a Kaiku y fue descalificado y no participó en la segunda jornada del campeonato. Su tiempo había sido de 21:11.6.",  # noqa: E501
            "Ur-Kirolak fue descalificado por abordar a Astillero en una ciaboga. Su tiempo había sido de 20:54.44.",
            "Santander fue descalificado por abordaje. Su tiempo había sido de 21:41.00",
            "Donibaneko fue descalificado por irrumpir en la calle de Orio. Su tiempo final había sido de 21:05.64.",
        ]
        results = [
            {
                "RIANXO": (None, Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "CABO DA CRUZ": ("21:25.130000", Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "SAMERTOLAMEU": ("20:17.820000", Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "SAMERTOLAMEU": ("19:07.890000", Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "PUEBLA": ("21:25.020000", Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "AMEGROVE": ("20:09.330000", Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "DONIBANEKO": ("20:59.350000", Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "TRINTXERPE": (None, Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "SANTANDER": ("21:11.600000", Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "UR KIROLAK": ("20:54.440000", Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "SANTANDER": ("21:41.000000", Penalty(disqualification=True, reason=COLLISION)),
            },
            {
                "DONIBANEKO": ("21:05.640000", Penalty(disqualification=True, reason=COLLISION)),
            },
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text), results[idx])

    def test_wrong_lineup_normalization(self):
        notes = [
            "Chapela quedó fuera de regata después de una reclamación por problemas con la ficha de uno de sus remeros (Guta Ionut). Perdió la cuarta plaza tras realizar un tiempo de 20:40.22.",  # noqa: E501
            "Bueu quedó fuera de regata por alineación indebida de remeros de Marín. Su tiempo había sido de 24:23.73.",
            "Raspas fue descalificado por llevar un remero con licencia de Santurtzi. Deusto-Portugalete B fue descalificado por llevar juveniles.",  # noqa: E501
            "Kaiku fue descalificado por alineación indebida, su tiempo había sido de 20:26.42.",
        ]
        results = [
            {
                "CHAPELA": ("20:40.220000", Penalty(disqualification=True, reason=WRONG_LINEUP)),
            },
            {
                "BUEU": ("24:23.730000", Penalty(disqualification=True, reason=WRONG_LINEUP)),
            },
            {
                "RASPAS": (None, Penalty(disqualification=True, reason=WRONG_LINEUP)),
                "DEUSTO-PORTUGALETE B": (None, Penalty(disqualification=True, reason=WRONG_LINEUP)),
            },
            {
                "KAIKU": ("20:26.420000", Penalty(disqualification=True, reason=WRONG_LINEUP)),
            },
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text), results[idx])

    def test_sinking_normalization(self):
        notes = [
            "Ares se hundió antes de la 3.ª ciaboga. A Cabana fue abordado por Perillo en la 1.ª ciaboga. El tiempo de Perillo había sido de 22:31.58",  # noqa: E501
        ]
        results = [
            {
                "ARES": (None, Penalty(disqualification=True, reason=SINKING)),
                "PERILLO": ("22:31.580000", Penalty(disqualification=True, reason=COLLISION)),
            },
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text), results[idx])

    def test_boat_weight_normalization(self):
        notes = [
            "Samertolameu fue descalificado por no pesar la embarcación. Su tiempo había sido de 21:07.34.",
        ]
        results = [
            {
                "SAMERTOLAMEU": ("21:07.340000", Penalty(disqualification=True, reason=BOAT_WEIGHT_LIMIT)),
            },
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text), results[idx])

    def test_is_race_cancelled(self):
        notes = [
            "La regata se anuló después de que Elantxobe impugnara porque una embarcación que cruzó el campo de regateo les molestó",  # noqa: E501
            "La regata fue anulada tras reclamar todos los equipos de la calle 5",  # noqa: E501
        ]
        for _, text in enumerate(notes):
            self.assertTrue(is_cancelled(text))
