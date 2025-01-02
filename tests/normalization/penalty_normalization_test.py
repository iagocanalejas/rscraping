import unittest
from datetime import time

from rscraping.data.constants import (
    BOAT_WEIGHT_LIMIT,
    COLLISION,
    DOPING,
    LACK_OF_COMPETITIVENESS,
    NULL_START,
    OFF_THE_FIELD,
    SINKING,
    STARBOARD_TACK,
    WRONG_LINEUP,
    WRONG_ROUTE,
)
from rscraping.data.models import Penalty
from rscraping.data.normalization import (
    is_absent,
    is_cancelled,
    is_guest,
    is_retired,
    normalize_penalty,
    retrieve_penalty_times,
)


class TestPenaltyNormalization(unittest.TestCase):
    def test_starboard_tack_normalization(self):
        notes = [
            "Vila de Cangas realizó la primera ciaboga por estribor.",
            "Vila de Cangas realizó la segunda ciaboga por estribor.",
            "Vila de Cangas tomó la segunda baliza por estribor.",
            "Ría de Marín realizó una ciaboga por estribor.",
            "Fortuna realizió una ciaboga por estribor",
            "Castro había dado la tercera ciaboga por estribor, siendo su tiempo de 21:48.3",
            "Castro ocupó la séptima posición pero fue descalificado por realizar la segunda ciaboga por estribor. Su tiempo había sido de 21:48.12.",  # noqa: E501
            "Castro fue descalificado por tomar la segunda ciaboga por estribor y no rectificar.",
            "Hondarribia tuvo que repetir una ciaboga por haberla dado por estribor.",
            "El tiempo de Algorta había sido de 20:08.0. Castro había dado la tercera ciaboga por estribor, siendo su tiempo de 21:48.3.",  # noqa: E501
            "Kaiku fue descalificado por realizar una ciaboga de forma incorrecta. Castropol estrenó una trainera de fibra, la primera de los astilleros Amilibia. Se recogió por la mañana en Orio y se remó por la tarde.",  # noqa: E501
        ]
        penalties = [
            {"VILA DE CANGAS": Penalty(disqualification=False, reason=STARBOARD_TACK)},
            {"VILA DE CANGAS": Penalty(disqualification=False, reason=STARBOARD_TACK)},
            {"VILA DE CANGAS": Penalty(disqualification=False, reason=STARBOARD_TACK)},
            {"RÍA DE MARÍN": Penalty(disqualification=False, reason=STARBOARD_TACK)},
            {"FORTUNA": Penalty(disqualification=False, reason=STARBOARD_TACK)},
            {"CASTRO": Penalty(disqualification=False, reason=STARBOARD_TACK)},
            {"CASTRO": Penalty(disqualification=True, reason=STARBOARD_TACK)},
            {"CASTRO": Penalty(disqualification=True, reason=STARBOARD_TACK)},
            {"HONDARRIBIA": Penalty(disqualification=False, reason=STARBOARD_TACK)},
            {"CASTRO": Penalty(disqualification=False, reason=STARBOARD_TACK)},
            {"KAIKU": Penalty(disqualification=True, reason=STARBOARD_TACK)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(penalties[idx].keys())), penalties[idx])

    def test_off_the_field_normalization(self):
        notes = [
            "San Simón y A Cabana pasaron la baliza de meta por estribor. El tiempo de San Simón había sido de 24:34.29 y el de A Cabana de 24:30.41.",  # noqa: E501
            "Cesantes y el Náutico de Vigo dejaron la baliza de meta por estribor. El tiempo de Cesantes había sido de 21:52.58 y el del Náutico de Vigo de 21:39.47.",  # noqa: E501
            "Castropol entró a meta fuera de línea (la línea de meta entre la baliza uno y la cinco). Su tiempo había sido de 24:52.57.",  # noqa: E501
            "Tirán fue descalificada por entrar en meta dejando la boya por estribor. Su tiempo había sido de 21:58.00.",  # noqa: E501
            "San Simón fue descalificado por dejar por estribor una baliza del recorrido y la meta.",
            "El tiempo de Tirán había sido 19:15.32, pero fue descalificado por dejar su baliza por estribor a la entrada a meta.",  # noqa: E501
            "Hondarribia fue descalificado por entrar en la baliza de Pedreña. Había realizado un tiempo de 21:57.",
            "Rianxo fue descalificado por dejar el puente por el arco equivocado. Su tiempo había sido de 18:58.91. El ganador de la bandera era quien tuviese menos tiempo en la jornada final",  # noqa: E501
        ]
        penalties = [
            {
                "SAN SIMÓN": Penalty(disqualification=True, reason=OFF_THE_FIELD),
                "CABANA": Penalty(disqualification=True, reason=OFF_THE_FIELD),
            },
            {
                "CESANTES": Penalty(disqualification=True, reason=OFF_THE_FIELD),
                "NÁUTICO DE VIGO": Penalty(disqualification=True, reason=OFF_THE_FIELD),
            },
            {"CASTROPOL": Penalty(disqualification=True, reason=OFF_THE_FIELD)},
            {"TIRÁN": Penalty(disqualification=True, reason=OFF_THE_FIELD)},
            {"SAN SIMÓN": Penalty(disqualification=True, reason=OFF_THE_FIELD)},
            {"TIRÁN": Penalty(disqualification=True, reason=OFF_THE_FIELD)},
            {"HONDARRIBIA": Penalty(disqualification=True, reason=OFF_THE_FIELD)},
            {"RIANXO": Penalty(disqualification=True, reason=OFF_THE_FIELD)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(penalties[idx].keys())), penalties[idx])

    def test_wrong_route_normalization(self):
        notes = [
            "Orio fue descalificado por cruzarse de calle.",
        ]
        penalties = [
            {"ORIO": Penalty(disqualification=True, reason=WRONG_ROUTE)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(penalties[idx].keys())), penalties[idx])

    def test_lack_of_competitiveness_normalization(self):
        notes = [
            "Se consideró que a Ondarroa le faltó voluntad de competir, infringiendo el artículo 39 del vigente Código de Regatas, que obliga a toda tripulación que tome la salida a remar a ritmo de regata hasta terminar.",  # noqa: E501
        ]
        results = [
            {"ONDARROA": Penalty(disqualification=True, reason=LACK_OF_COMPETITIVENESS)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(results[idx].keys())), results[idx])

    def test_null_start_normalization(self):
        notes = [
            "Virxe da Guía tuvo dos salidas nulas.",
            "Tirán compitió fuera de regata por salidas nulas. Su tiempo había sido de 20:55.",
            "Fortuna quedó fuera de regata en la primera jornada por llegar tarde a la salida.",
            'San Juan debería haber salido al minuto de la "Lugañene", pero no se presentó en la baliza de salida, al parecer por un malentendido de su delegado. El tiempo fue de 21:19.85.',  # noqa: E501
        ]
        penalties = [
            {"VIRXE DA GUÍA": Penalty(disqualification=True, reason=NULL_START)},
            {"TIRÁN": Penalty(disqualification=True, reason=NULL_START)},
            {"FORTUNA": Penalty(disqualification=True, reason=NULL_START)},
            {"SAN JUAN": Penalty(disqualification=True, reason=NULL_START)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(penalties[idx].keys())), penalties[idx])

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
            "Ur-Kirolak fue descalificado por abordar a Astillero en una ciaboga. Su tiempo había sido de 20:54.44.",
            "Santander fue descalificado por abordaje. Su tiempo había sido de 21:41.00",
            "Donibaneko fue descalificado por irrumpir en la calle de Orio. Su tiempo final había sido de 21:05.64.",
            "Hondarribia fue descalificado por invadir la calle de Santurtzi. Su tiempo fue de 21:55.99.",
            "Santander fue descalificado por invadir la calle contraria.",
            "Castropol se chocó contra La Coruña.",
            "En la tercera ciaboga Castro fue abordado por Pedreña, cuando iban primeros.",
            "Se clasificaban cuatro para la final, y los cuatro siguientes para el trofeo Federación. Donibaneko y San Pedro volvieron a impugnar al volver a presentarse Orio con la trainera de fibra. San Pedro colisionó con Donibaneko tras efectuar el viraje de la última ciaboga.",  # noqa: E501
            "En la primera jornada, Santander había llegado junto a Astillero en el segundo puesto de tanda, pero abordó a Kaiku y fue descalificado y no participó en la segunda jornada del campeonato. Su tiempo había sido de 21:11.6.",  # noqa: E501
            "Hondarribia se retiró tras colisionar con Santoña.",
        ]
        penalties = [
            {"RIANXO": Penalty(disqualification=True, reason=COLLISION)},
            {"CABO DA CRUZ": Penalty(disqualification=True, reason=COLLISION)},
            {"SAMERTOLAMEU": Penalty(disqualification=True, reason=COLLISION)},
            {"SAMERTOLAMEU": Penalty(disqualification=True, reason=COLLISION)},
            {"PUEBLA": Penalty(disqualification=True, reason=COLLISION)},
            {"AMEGROVE": Penalty(disqualification=True, reason=COLLISION)},
            {"DONIBANEKO": Penalty(disqualification=True, reason=COLLISION)},
            {"TRINTXERPE": Penalty(disqualification=True, reason=COLLISION)},
            {"UR KIROLAK": Penalty(disqualification=True, reason=COLLISION)},
            {"SANTANDER": Penalty(disqualification=True, reason=COLLISION)},
            {"DONIBANEKO": Penalty(disqualification=True, reason=COLLISION)},
            {"HONDARRIBIA": Penalty(disqualification=True, reason=COLLISION)},
            {"SANTANDER": Penalty(disqualification=True, reason=COLLISION)},
            {"CASTROPOL": Penalty(disqualification=True, reason=COLLISION)},
            {"PEDREÑA": Penalty(disqualification=True, reason=COLLISION)},
            {"SAN PEDRO": Penalty(disqualification=True, reason=COLLISION)},
            {"SANTANDER": Penalty(disqualification=True, reason=COLLISION)},
            {"HONDARRIBIA": Penalty(disqualification=True, reason=COLLISION)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(penalties[idx].keys())), penalties[idx])

    def test_wrong_lineup_normalization(self):
        notes = [
            "Chapela quedó fuera de regata después de una reclamación por problemas con la ficha de uno de sus remeros (Guta Ionut). Perdió la cuarta plaza tras realizar un tiempo de 20:40.22.",  # noqa: E501
            "Bueu quedó fuera de regata por alineación indebida de remeros de Marín. Su tiempo había sido de 24:23.73.",
            "Raspas fue descalificado por llevar un remero con licencia de Santurtzi. Deusto-Portugalete B fue descalificado por llevar juveniles.",  # noqa: E501
            "Kaiku fue descalificado por alineación indebida, su tiempo había sido de 20:26.42.",
            "Kaiku ganó con una ventaja de 59 segundos, pero tenía remeros con ficha de Orio.",
        ]
        penalties = [
            {"CHAPELA": Penalty(disqualification=True, reason=WRONG_LINEUP)},
            {"BUEU": Penalty(disqualification=True, reason=WRONG_LINEUP)},
            {
                "RASPAS": Penalty(disqualification=True, reason=WRONG_LINEUP),
                "DEUSTO - PORTUGALETE B": Penalty(disqualification=True, reason=WRONG_LINEUP),
            },
            {"KAIKU": Penalty(disqualification=True, reason=WRONG_LINEUP)},
            {"KAIKU": Penalty(disqualification=True, reason=WRONG_LINEUP)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(penalties[idx].keys())), penalties[idx])

    def test_doping_normalization(self):
        notes = [
            "El tiempo de Yola había sido de 23:16.95, pero su remero Patxi Aldasoro no pasó el control antidoping y fueron descalificados.",  # noqa: E501
        ]
        penalties = [
            {"YOLA": Penalty(disqualification=True, reason=DOPING)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(penalties[idx].keys())), penalties[idx])

    def test_sinking_normalization(self):
        notes = [
            "Ares se hundió antes de la 3.ª ciaboga. A Cabana fue abordado por Perillo en la 1.ª ciaboga. El tiempo de Perillo había sido de 22:31.58",  # noqa: E501
            "Raspas se retiró por entrar agua en su embarcación.",
        ]
        penalties = [
            {
                "ARES": Penalty(disqualification=False, reason=SINKING),
                "PERILLO": Penalty(disqualification=True, reason=COLLISION),
            },
            {"RASPAS": Penalty(disqualification=False, reason=SINKING)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(penalties[idx].keys())), penalties[idx])

    def test_boat_weight_normalization(self):
        notes = [
            "Samertolameu fue descalificado por no pesar la embarcación. Su tiempo había sido de 21:07.34.",
        ]
        penalties = [
            {"SAMERTOLAMEU": Penalty(disqualification=True, reason=BOAT_WEIGHT_LIMIT)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(penalties[idx].keys())), penalties[idx])

    def test_unknown_penalty_normalization(self):
        notes = [
            "Donostia Arraun Lagunak fue descalificado, su tiempo había sido de 20:58.16.",
            "La primera jornada se tuvo que anular por el mal estado de la mar. El ganador se adjudicó también el III trofeo Manolo Santamaría y la VIII Copa del Rey. La primera tanda sirvió como Campeonato Regional. Santoñés realizó un tiempo de 20:33.0, pero fue descalificado.",  # noqa: E501
        ]
        penalties = [
            {"DONOSTIA ARRAUN LAGUNAK": Penalty(disqualification=True, reason=None)},
            {"SANTOÑÉS": Penalty(disqualification=True, reason=None)},
        ]
        for idx, text in enumerate(notes):
            self.assertEqual(normalize_penalty(text, list(penalties[idx].keys())), penalties[idx])

    def test_retrieve_participant_times(self):
        notes = [
            "El tiempo de Vilaxoan fue de 26:16.00.",
            "El tiempo de Raspas había sido 23:41.86.",
            "El tiempo de Arkote había sido de 21:48.40.",
            "El tiempo de Donostia Arraun Lagunak había sido de 22:19.00.",
            "El tiempo de Lutxana había sido de 21:14.58, mientras el de Raspas fue de 21:05.37.",
            "El tiempo de Coruxo había sido de 22:32.16. El tiempo de Puebla había sido de 22:16.98.",
            "El tiempo de Portugalete había sido de 21:29.20, el de Santurtzi de 21:15.50, el de Trinxerpe de 20:35.00 y el de Zarautz de 20:57.70.",  # noqa: E501
            "El tiempo de Tirán había sido de 19:23.52, el de Mecos de 19:31.32 y el de Cabo da Cruz de 19:13.70.",
            "El tiempo de Amegrove había sido de 20:09.33, pero fue descalificada por invasión de la calle del Náutico de Vigo a la salida de la segunda ciaboga.",  # noqa: E501
            "El tiempo de Camargo había sido de 21:02.84 y el de Pedreña de 21:09.46. Fueron descalificados por no dar el peso mínimo de la trainera.",  # noqa: E501
            "El tiempo final de Camargo había sido de 21:48,00, pero tenía en su tripulación un juvenil que ya había remado tres regatas en el mismo año.",  # noqa: E501
            "Hondarribia fue descalificado por entrar en la baliza de Pedreña. Había realizado un tiempo de 21:57.",
            "Arraun Lagunak tuvo un tiempo de 21:21.02.",
            "Hondarribia había realizado un tiempo de 20:29.1.",
            # -- MULTIPLE TIMES --
            "Perillo B y Mecos B formaban parte de una tanda de promoción, sus tiempos fueron de 19:52 y 19:58, respectivamente.",  # noqa: E501
            "Getaria, Arkote, Hernani y Fortuna formaban parte de una tanda de promoción, sus tiempos fueron de 21:27.12, 21:40.03, 22:20.12 y 22:42.34, respectivamente",  # noqa: E501
            "Donibaneko B y San Juan B participaban en una tanda de promoción, por eso aparecen fuera de regata. El tiempo de Donibaneko B ue de 20:40.36, mientras que San Juan B hizo 20:42.84. Antes",  # noqa: E501
            "Las cuatro primeras clasificadas disputarían el año siguiente la Liga A, mientras el resto participarían en la B. Las cuatro traineras fuera de regata habían sido invitadas. Santiagotarrak marcó un tiempo de 22:09.61, Fortuna de 22:01.71, Elantxobe de 21:53.86 y Koxtape B de 21:00.07.",  # noqa: E501
            "San Simón y A Cabana pasaron la baliza de meta por estribor. El tiempo de San Simón había sido de 24:34.29 y el de A Cabana de 24:30.41.",  # noqa: E501
            "Cesantes y el Náutico de Vigo dejaron la baliza de meta por estribor. El tiempo de Cesantes había sido de 21:52.58 y el del Náutico de Vigo de 21:39.47.",  # noqa: E501
            # -- DISCUALIFICATION + TIME --
            "Donostia Arraun Lagunak fue descalificado, su tiempo había sido de 20:58.16.",
            "La primera jornada se tuvo que anular por el mal estado de la mar. El ganador se adjudicó también el III trofeo Manolo Santamaría y la VIII Copa del Rey. La primera tanda sirvió como Campeonato Regional. Santoñés realizó un tiempo de 20:33.0, pero fue descalificado.",  # noqa: E501
            "El tiempo de Algorta había sido de 20:08.0. Castro había dado la tercera ciaboga por estribor, siendo su tiempo de 21:48.3.",  # noqa: E501
            "Castro había dado la tercera ciaboga por estribor, siendo su tiempo de 21:48.3",
            'San Juan debería haber salido al minuto de la "Lugañene", pero no se presentó en la baliza de salida, al parecer por un malentendido de su delegado. El tiempo fue de 21:19.85.',  # noqa: E501
            "Samertolameu estorbó a Bueu en la tercera virada. Su tiempo había sido el mejor con 19:07.89.",
            "En la segunda jornada Donibaneko fue descalificado por invadir la calle de Santurtzi en la segunda ciaboga. Terminó con un tiempo de 20:59,35.",  # noqa: E501
            "Chapela quedó fuera de regata después de una reclamación por problemas con la ficha de uno de sus remeros (Guta Ionut). Perdió la cuarta plaza tras realizar un tiempo de 20:40.22.",  # noqa: E501
            "Rianxo fue descalificado por dejar el puente por el arco equivocado. Su tiempo había sido de 18:58.91. El ganador de la bandera era quien tuviese menos tiempo en la jornada final",  # noqa: E501
        ]
        results = [
            {"VILAXOAN": time(0, 26, 16)},
            {"RASPAS": time(0, 23, 41, 860000)},
            {"ARKOTE": time(0, 21, 48, 400000)},
            {"DONOSTIA ARRAUN LAGUNAK": time(0, 22, 19)},
            {"LUTXANA": time(0, 21, 14, 580000), "RASPAS": time(0, 21, 5, 370000)},
            {"CORUXO": time(0, 22, 32, 160000), "PUEBLA": time(0, 22, 16, 980000)},
            {
                "PORTUGALETE": time(0, 21, 29, 200000),
                "SANTURTZI": time(0, 21, 15, 500000),
                "TRINXERPE": time(0, 20, 35),
                "ZARAUTZ": time(0, 20, 57, 700000),
            },
            {
                "TIRÁN": time(0, 19, 23, 520000),
                "MECOS": time(0, 19, 31, 320000),
                "CABO DA CRUZ": time(0, 19, 13, 700000),
            },
            {"AMEGROVE": time(0, 20, 9, 330000)},
            {"CAMARGO": time(0, 21, 2, 840000), "PEDREÑA": time(0, 21, 9, 460000)},
            {"CAMARGO": time(0, 21, 48)},
            {"": time(0, 21, 57)},
            {"ARRAUN LAGUNAK": time(0, 21, 21, 20000)},
            {"HONDARRIBIA": time(0, 20, 29, 100000)},
            {"PERILLO B": time(0, 19, 52), "MECOS B": time(0, 19, 58)},
            {
                "GETARIA": time(0, 21, 27, 120000),
                "ARKOTE": time(0, 21, 40, 30000),
                "HERNANI": time(0, 22, 20, 120000),
                "FORTUNA": time(0, 22, 42, 340000),
            },
            {"DONIBANEKO B": time(0, 20, 40, 360000), "SAN JUAN B": time(0, 20, 42, 840000)},
            {
                "SANTIAGOTARRAK": time(0, 22, 9, 610000),
                "FORTUNA": time(0, 22, 1, 710000),
                "ELANTXOBE": time(0, 21, 53, 860000),
                "PASAI DONIBANE KOXTAPE B": time(0, 21, 0, 70000),
            },
            {"SAN SIMÓN": time(0, 24, 34, 290000), "CABANA": time(0, 24, 30, 410000)},
            {"CESANTES": time(0, 21, 52, 580000), "NÁUTICO DE VIGO": time(0, 21, 39, 470000)},
            {"": time(0, 20, 58, 160000)},
            {"SANTOÑÉS": time(0, 20, 33)},
            {"ALGORTA": time(0, 20, 8), "": time(0, 21, 48, 300000)},
            {"": time(0, 21, 48, 300000)},
            {"": time(0, 21, 19, 850000)},
            {"": time(0, 19, 7, 890000)},
            {"": time(0, 20, 59, 350000)},
            {"": time(0, 20, 40, 220000)},
            {"": time(0, 18, 58, 910000)},
        ]
        self.assertEqual(len(notes), len(results))
        for i, text in enumerate(notes):
            self.assertEqual(retrieve_penalty_times(text), results[i])

    def test_cancelled(self):
        notes = [
            "La regata se suspendió en los primeros compases de la segunda tanda, después de varios retrasos en la salida de la prueba.",  # noqa: E501
            "La regata se anuló después de que Elantxobe impugnara porque una embarcación que cruzó el campo de regateo les molestó",  # noqa: E501
            "La regata fue anulada tras reclamar todos los equipos de la calle 5",
            "Esta prueba fue suspendida por vendaval.",
            "Por el mal tiempo la segunda tanda no salió y se dio por ganador a Coruxo. Los premios se repartieron a partes iguales entre los ocho.",  # noqa: E501
            "Tras haberse disputado la primera tanda a contra reloj por la mala mar, se observó que una de las balizas se desató y no se pudo recuperar. Debido a este inconveniente se decidió anular la regata para la liga, otorgando a Castropol la bandera por haberse disputado parte de la prueba.",  # noqa: E501
            "La regata fue anulada tras reclamar todos los equipos de la calle 5. Se midió y como resultado dio 184 metros de más. El campeonato se celebró al tiempo que la Bandera Villa de Bilbao 2000.",  # noqa: E501
            "La regata fue anulada por la galerna. Era la tercera jornada de la Liga Vasca. Se disputaron la primera y segunda tanda y debido al temporal se suspendió.",  # noqa: E501
        ]
        for text in notes:
            if not is_cancelled(text):
                self.fail(text)

    def test_retired(self):
        notes = [
            (
                "SANTURTZI",
                "Debido a las irregularidades del campo de regatas, Santurtzi no quiso participar y se retiró.",
            ),
            (
                "RASPAS",
                "Raspas se retiró por entrar agua en su embarcación.",
            ),
            (
                "ZIERBENA",
                "Zierbena no tomó la salida por considerar que el campo era irregular y que algunas calles eran mayores que otras.",  # noqa: E501
            ),
            (
                "ALGORTA",
                "Estaba prevista la celebración de la prueba los días 27 y 28 de agosto pero las inundaciones impidieron que así fuera. Algorta abandonó la prueba.",  # noqa: E501
            ),
        ]
        for participant, text in notes:
            if not is_retired(participant, text):
                self.fail(text)

    def test_guest(self):
        notes = [
            (
                "PERILLO B",
                "Perillo B y Mecos B formaban parte de una tanda de promoción, sus tiempos fueron de 19:52 y 19:58, respectivamente.",  # noqa: E501,
            ),
            (
                "ARKOTE",
                "Getaria, Arkote, Hernani y Fortuna formaban parte de una tanda de promoción, sus tiempos fueron de 21:27.12, 21:40.03, 22:20.12 y 22:42.34, respectivamente",  # noqa: E501
            ),
            (
                "DONIBANEKO B",
                "Donibaneko B y San Juan B participaban en una tanda de promoción, por eso aparecen fuera de regata. El tiempo de Donibaneko B ue de 20:40.36, mientras que San Juan B hizo 20:42.84. Antes",  # noqa: E501
            ),
            (
                "ISUNTZA",
                "La regata formaba parte de la Liga Vasca A, por lo que Getxo, Bermeo, Santurtzi, Lutxna, Isuntza, Elantxobe y Donostia Arraun Lagunak no puntuaban.",  # noqa: E501
            ),
            (
                "CASTRO B",
                "Se trataba de una regata de la Liga Vasca B, pero Castro, Castro B, La Maruca, Pontejos, Colindres, Santander, Camargo y Castropol no puntuaban.",  # noqa: E501
            ),
            # (
            #     "ELANTXOBE",
            #     "Las cuatro primeras clasificadas disputarían el año siguiente la Liga A, mientras el resto participarían en la B. Las cuatro traineras fuera de regata habían sido invitadas. Santiagotarrak marcó un tiempo de 22:09.61, Fortuna de 22:01.71, Elantxobe de 21:53.86 y Koxtape B de 21:00.07.",  # noqa: E501
            # ),
        ]
        for participant, text in notes:
            if not is_guest(participant, text):
                self.fail(text)

    def test_absent(self):
        notes = [
            ("LAREDO", "Estaba prevista la participación de Laredo pero no se presentó."),
        ]
        for participant, text in notes:
            if not is_absent(participant, text):
                self.fail(text)

    def test_no_penalty(self):
        notes = [
            "Donibaneko utilizó la trainera de madera en lugar de la de fibra. Orio compitió con una trainera de fibra construida por la firma Compoplás.",  # noqa: E501
            "El mal estado de la mar hizo que las traineras colocaran sus palcas de proa a popa.",
            "El segundo premio se dio a la familia de Juan Manuel Santisteban, ciclista de Colindres fallecido en una caída en el Giro de Italia.",  # noqa: E501
            "En esta prueba hubo fuerte viento del noroeste y se realizó en el muelle de Arriluze.",
            "En esta regata reapareció Zierbena tras 19 años de inactividad.",
            "En la segunda ciaboga Arkote perdió al proel.",
            "Estaba anunciada para el 1 de julio pero se aplazó.",
            "Estaba prevista la celebración el día 7, pero no fue posible colocar las balizas interiores por el fuerte viento y mar de fondo. Zumaia se retiró por precaución, ya que algunos remeros no sabían nadar y el estado de la mar presentaba sus dificultades.",  # noqa: E501
            "Fortuna tuvo que remar en solitario al llegar tarde para participar en la 1.ª tanda, debido al intenso tráfico entre Zarautz y Getaria.",  # noqa: E501
            "Hubo polémica con la medición de las calles tres y cuatro en balizas exteriores, ya que no guardaban relación con las interiores.",  # noqa: E501
            "Itxaspe estaba compuesto por los remeros de San Juan B y Yola por los de Donibaneko B. Tenían que salir con el nombre de otra institución porque no se permitían segundas tripulaciones.",  # noqa: E501
            "Kaiku también ganó 10 remos de trainera y un trofeo, mientras Portugalete ganó 5 remos de trainera.",
            "Kaiku y Astillero le prestaron una trainera a Castropol para competir.",
            "La bandera fue donada por los comerciantes del casco viejo de Bilbao.",
            "La regata era puntuable para la Liga B pero una de las boyas se desplazó y pasó a no ser puntuable.",
            "La selección gallega estaba compuesta por remeras de Bueu, Cabo y Samertolameu.",
            "Las traineras tuvieron que rodear la isla para enfilar hacia Ondarroa debido a la media marea.",
            "La victoria de Donibaneko no estuvo exenta de polémica debido al retraso acumulado, producido por las embarcaciones de recreo que invadieron el campo de regatas.",  # noqa: E501
            "Los árbitros cántabros hicieron boicot y se negaron a participar en la organización de la competición, debido a que en la Sotileza los castreños robaron la bandera de la tribuna.",  # noqa: E501
            "No acudieron los barcos de la Liga ACT por tener regata en Galicia.",
            "Orio se adjudicó la II Bandera del Real Astillero de Guarnizo.",
            "Para las tripulaciones vizcaínas dicha regata era clasificatoria para el Campeonato de Bizkaia y para la Liga de traineras. Organizada por el Club de remo de Algorta a la altura del muelle de Arriluze.",  # noqa: E501
            "Prevista para el 25 de julio, tuvo que aplazarse por el temporal. Victoria impugnada por San Pedro y Donibaneko con el argumento de que es antireglamentario el suplemento de la parte alta del carel a",  # noqa: E501
            'Regata con "metas volantes". Causó confusión y no se volvió a utilizar.',
            "Se clasificaban únicamente las cinco primeras en esta regata, más el campeón guipuzcoano. Los dos últimos se enfrentaban a vizcaínos y cántabros. Se trataba de la continuación al Memorial Sagarzazu de 1971.",  # noqa: E501
            "Se clasifican los cinco primeros.",
            "Se otorgaron subvenciones y no se dieron premios.",
            'Se puso en juego también una bandera que llevaba bordado "Fiestas Euskaras 1925-1975". Fue también un homanaje a Lertxundi y Zabala, remeros de Lasarte que fallecieron en un entrenamiento en Orio.',  # noqa: E501
            "Se redujo la distancia de las tres millas debido al estado de la mar.",
            "Se retrasó la regata motivado por el desplazamiento de uno de los trenes de balizaje del campo.",
            "Urdaibai obtuvo 11 puntos en la regata, pero tenía una sanción de 95 puntos en esta temporada.",
            "Ur-Kirolak, Astillero y Camargo fueron amonestados por llegar tarde a la salida.",
            "Hondarribia B llevó a los suplentes para dar descanso a los titulares.",
            "Esta prueba se realizó a contrarreloj por el mal estado de la mar.",
        ]
        for text in notes:
            if normalize_penalty(text, []) != {}:
                self.fail(text)
