__LEAGUES_MAP = {
    'LIGA GALEGA DE TRAIÑAS': ['LGT'],
    'LIGA GALEGA DE TRAIÑAS A': ['LIGA A'],
    'LIGA GALEGA DE TRAIÑAS B': ['LIGA B'],
    'LIGA GALEGA DE TRAIÑAS FEMENINA': ['LIGA FEM', 'LIGA F'],
    'ASOCIACIÓN DE CLUBES DE TRAINERAS': ['ACT'],
}


def normalize_league_name(name: str) -> str:
    for k, v in __LEAGUES_MAP.items():
        if name in v:
            name = k
            break
    return name
