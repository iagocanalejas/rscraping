import pytest

from rscraping.data.normalization import normalize_name_parts, normalize_race_name, remove_day_indicator


@pytest.mark.parametrize(
    ("name, result_normalized, result_parts"),
    [
        (
            "XXXVIII. El Correo Ikurriña - Kutxabank SN - Lekeitioko Udala",
            "XXXVIII EL CORREO IKURRIÑA - KUTXABANK SARI NAGUSIA - LEKEITIOKO UDALA",
            [("EL CORREO IKURRIÑA", 38), ("KUTXABANK SARI NAGUSIA", None), ("LEKEITIOKO UDALA", None)],
        ),
        (
            "Hondarribiko XXXVI. Bandera / Mapfre Sari Nagusia",
            "HONDARRIBIKO XXXVI BANDERA - MAPFRE SARI NAGUSIA",
            [("HONDARRIBIKO BANDERA", 36), ("MAPFRE SARI NAGUSIA", None)],
        ),
        (
            "Orioko XXXIII. Estropada - Orio Kanpina XI. Bandera",
            "ORIOKO XXXIII ESTROPADA - ORIO KANPINA XI BANDERA",
            [("ORIOKO ESTROPADA", 33), ("ORIO KANPINA BANDERA", 11)],
        ),
        (
            "Getxoko Estropaden XLV. Ikurriña - J.A. Agirre Lehendakariaren XIX. Omenaldia",
            "GETXOKO ESTROPADEN XLV IKURRIÑA - JOSE ANTONIO AGIRRE LEHENDAKARIAREN XIX OMENALDIA",
            [("GETXOKO ESTROPADEN IKURRIÑA", 45), ("JOSE ANTONIO AGIRRE LEHENDAKARIAREN OMENALDIA", 19)],
        ),
        (
            "XVIII BANDEIRA CIDADE DE FERROL VIII MEMORIAL MIGUEL DERUNGS CRIADO",
            "XVIII BANDEIRA CIDADE DE FERROL VIII MEMORIAL MIGUEL DERUNGS CRIADO",
            [("BANDEIRA CIDADE DE FERROL", 18), ("MEMORIAL MIGUEL DERUNGS CRIADO", 8)],
        ),
        (
            "X BANDERA ILLA DO SAMERTOLAMEU-FANDICOSTA",
            "X BANDEIRA ILLA DO SAMERTOLAMEU - FANDICOSTA",
            [("BANDEIRA ILLA DO SAMERTOLAMEU - FANDICOSTA", 10)],
        ),
        (
            "CAMPEONATO DE GUIPÚZCOA",
            "CAMPEONATO DE GIPÚZKOA",
            [("CAMPEONATO DE GIPÚZKOA", None)],
        ),
        (
            "BANDERA CONCELLO DE BUEU (ACT)",
            "BANDERA CONCELLO DE BUEU",
            [("BANDERA CONCELLO DE BUEU", None)],
        ),
        (
            "ASOCIACIÓN DE REMO DEL CANTÁBRICO 2:BANDERA VILLA DE LAREDO",
            "BANDERA VILLA DE LAREDO",
            [("BANDERA VILLA DE LAREDO", None)],
        ),
        (
            "REGATA LIGA GALEGA DE TRAINERAS A",
            "REGATA LIGA GALEGA DE TRAINERAS A",
            [("REGATA LIGA GALEGA DE TRAINERAS A", None)],
        ),
        (
            "BANDERA EUSKADI BASQUE-COUNTRY",
            "BANDERA EUSKADI BASQUE COUNTRY",
            [("BANDERA EUSKADI BASQUE COUNTRY", None)],
        ),
        (
            "XV. BILBOKO BANDERA - BANDERA DE BILBAO (13-07-2024)",
            "XV BANDERA DE BILBAO",
            [("BANDERA DE BILBAO", 15)],
        ),
        (
            "CLASIFICATORIA ARC",
            "CLASIFICATORIA ARC",
            [("CLASIFICATORIA ARC", None)],
        ),
        (
            "BANDERA CONCELLO DE VILAGARCÍA",
            "BANDERA CONCELLO DE VILAGARCÍA",
            [("BANDERA CONCELLO DE VILAGARCÍA", None)],
        ),
        (
            "BANDERA BILBAO 716 ANIVERSARIO",
            "BANDERA DE BILBAO",
            [("BANDERA DE BILBAO", None)],
        ),
        (
            "BANDERA WOFCO",
            "BANDERA WOFCO",
            [("BANDERA WOFCO", None)],
        ),
        (
            "BANDERA CIUDAD DE RIVEIRA",
            "BANDERA CIUDAD DE RIVEIRA",
            [("BANDERA CIUDAD DE RIVEIRA", None)],
        ),
        (
            "REGATA LIGA ARC",
            "REGATA LIGA ARC",
            [("REGATA LIGA ARC", None)],
        ),
        (
            "EMAKUMEEN BILBOKO XI IKURRIÑA - ANE AIZPURUREN VI OROIMENA",
            "XI BANDERA DE BILBAO",
            [("BANDERA DE BILBAO", 11)],
        ),
    ],
)
def test_name_parts_normalization(name, result_normalized, result_parts) -> None:
    normalized = normalize_race_name(name)
    assert normalized == result_normalized
    assert normalize_name_parts(normalized) == result_parts


@pytest.mark.parametrize(("name, expected"), [("PLAY-OFF LGT XORNADA 2 (ARES)", "PLAY-OFF LGT (ARES)")])
def test_remove_day_indicator(name, expected) -> None:
    assert remove_day_indicator(name) == expected
