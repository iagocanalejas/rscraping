import pytest

from rscraping.data.normalization import normalize_name_parts, normalize_race_name, remove_day_indicator


@pytest.mark.parametrize(
    ("name, expected"),
    [
        (
            "XXXVIII. El Correo Ikurriña - Kutxabank SN - Lekeitioko Udala",
            "XXXVIII EL CORREO IKURRIÑA - KUTXABANK SARI NAGUSIA - LEKEITIOKO UDALA",
        ),
        (
            "Hondarribiko XXXVI. Bandera / Mapfre Sari Nagusia",
            "HONDARRIBIKO XXXVI BANDERA - MAPFRE SARI NAGUSIA",
        ),
        (
            "Orioko XXXIII. Estropada - Orio Kanpina XI. Bandera",
            "ORIOKO XXXIII ESTROPADA - ORIO KANPINA XI BANDERA",
        ),
        (
            "Getxoko Estropaden XLV. Ikurriña - J.A. Agirre Lehendakariaren XIX. Omenaldia",
            "GETXOKO ESTROPADEN XLV IKURRIÑA - JOSE ANTONIO AGIRRE LEHENDAKARIAREN XIX OMENALDIA",
        ),
        (
            "XVII BANDEIRA CIDADE DE FERROL III MEMORIAL MIGUEL DERUNGS CRIADO",
            "XVII BANDEIRA CIDADE DE FERROL III MEMORIAL MIGUEL DERUNGS CRIADO",
        ),
        (
            "X BANDERA ILLA DO SAMERTOLAMEU-FANDICOSTA",
            "X BANDEIRA ILLA DO SAMERTOLAMEU - FANDICOSTA",
        ),
        (
            "CAMPEONATO DE GUIPÚZCOA",
            "CAMPEONATO DE GIPÚZKOA",
        ),
        (
            "BANDERA CONCELLO DE BUEU (ACT)",
            "BANDERA CONCELLO DE BUEU",
        ),
        (
            "ASOCIACIÓN DE REMO DEL CANTÁBRICO 2:BANDERA VILLA DE LAREDO",
            "BANDERA VILLA DE LAREDO",
        ),
        (
            "REGATA LIGA GALEGA DE TRAINERAS A",
            "REGATA LIGA GALEGA DE TRAINERAS A",
        ),
        (
            "BANDERA EUSKADI BASQUE-COUNTRY",
            "BANDERA EUSKADI BASQUE COUNTRY",
        ),
        (
            "XV. BILBOKO BANDERA - BANDERA DE BILBAO (13-07-2024)",
            "XV BANDERA DE BILBAO",
        ),
        (
            "CLASIFICATORIA ARC",
            "CLASIFICATORIA ARC",
        ),
        (
            "BANDERA CONCELLO DE VILAGARCÍA",
            "BANDERA CONCELLO DE VILAGARCÍA",
        ),
        (
            "BANDERA BILBAO 716 ANIVERSARIO",
            "BANDERA BILBAO 716 ANIVERSARIO",
        ),
        (
            "BANDERA WOFCO",
            "BANDERA WOFCO",
        ),
        (
            "BANDERA CIUDAD DE RIVEIRA",
            "BANDERA CIUDAD DE RIVEIRA",
        ),
        (
            "REGATA LIGA ARC",
            "REGATA LIGA ARC",
        ),
        (
            "BANDERA EXMO. AYTO. DE LAREDO",
            "BANDERA EXCELENTISIMO AYUNTAMIENTO DE LAREDO",
        ),
    ],
)
def test_race_name_normalization(name, expected) -> None:
    assert normalize_race_name(name) == expected


@pytest.mark.parametrize(
    ("name, expected"),
    [
        (
            "XXXVIII. El Correo Ikurriña - Kutxabank SN - Lekeitioko Udala",
            [("EL CORREO IKURRIÑA", 38), ("KUTXABANK SARI NAGUSIA", None), ("LEKEITIOKO UDALA", None)],
        ),
        (
            "Hondarribiko XXXVI. Bandera / Mapfre Sari Nagusia",
            [("HONDARRIBIKO BANDERA", 36), ("MAPFRE SARI NAGUSIA", None)],
        ),
        (
            "Orioko XXXIII. Estropada - Orio Kanpina XI. Bandera",
            [("ORIOKO ESTROPADA", 33), ("ORIO KANPINA BANDERA", 11)],
        ),
        (
            "Getxoko Estropaden XLV. Ikurriña - J.A. Agirre Lehendakariaren XIX. Omenaldia",
            [("GETXOKO ESTROPADEN IKURRIÑA", 45), ("JOSE ANTONIO AGIRRE LEHENDAKARIAREN OMENALDIA", 19)],
        ),
        (
            "XVIII BANDEIRA CIDADE DE FERROL VIII MEMORIAL MIGUEL DERUNGS CRIADO",
            [("BANDEIRA CIDADE DE FERROL", 18), ("MEMORIAL MIGUEL DERUNGS CRIADO", 8)],
        ),
        (
            "X BANDERA ILLA DO SAMERTOLAMEU-FANDICOSTA",
            [("BANDEIRA ILLA DO SAMERTOLAMEU - FANDICOSTA", 10)],
        ),
        (
            "CAMPEONATO DE GUIPÚZCOA",
            [("CAMPEONATO DE GIPÚZKOA", None)],
        ),
        (
            "BANDERA CONCELLO DE BUEU (ACT)",
            [("BANDERA CONCELLO DE BUEU", None)],
        ),
        (
            "ASOCIACIÓN DE REMO DEL CANTÁBRICO 2:BANDERA VILLA DE LAREDO",
            [("BANDERA VILLA DE LAREDO", None)],
        ),
        (
            "REGATA LIGA GALEGA DE TRAINERAS A",
            [("REGATA LIGA GALEGA DE TRAINERAS A", None)],
        ),
        (
            "BANDERA EUSKADI BASQUE-COUNTRY",
            [("BANDERA EUSKADI BASQUE COUNTRY", None)],
        ),
        (
            "XV. BILBOKO BANDERA - BANDERA DE BILBAO (13-07-2024)",
            [("BANDERA DE BILBAO", 15)],
        ),
        (
            "CLASIFICATORIA ARC",
            [("CLASIFICATORIA ARC", None)],
        ),
        (
            "BANDERA CONCELLO DE VILAGARCÍA",
            [("BANDERA CONCELLO DE VILAGARCÍA", None)],
        ),
        (
            "BANDERA BILBAO 716 ANIVERSARIO",
            [("BANDERA BILBAO 716 ANIVERSARIO", None)],
        ),
        (
            "BANDERA WOFCO",
            [("BANDERA WOFCO", None)],
        ),
        (
            "BANDERA CIUDAD DE RIVEIRA",
            [("BANDERA CIUDAD DE RIVEIRA", None)],
        ),
        (
            "REGATA LIGA ARC",
            [("REGATA LIGA ARC", None)],
        ),
    ],
)
def test_name_parts_normalization(name, expected) -> None:
    assert normalize_name_parts(normalize_race_name(name)) == expected


@pytest.mark.parametrize(("name, expected"), [("PLAY-OFF LGT XORNADA 2 (ARES)", "PLAY-OFF LGT (ARES)")])
def test_remove_day_indicator(name, expected) -> None:
    assert remove_day_indicator(name) == expected
