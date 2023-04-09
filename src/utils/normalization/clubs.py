import logging

from ai_django.ai_core.utils.strings import whitespaces_clean, remove_parenthesis

logger = logging.getLogger(__name__)

# list of normalizations to specific to be implemented
__ENTITY_TITLES = ['CR', 'SD', 'SDR', 'CM', 'CR', 'AD', 'CC', 'CDM', 'CCD', 'CRN', 'FEM', 'B']
__NORMALIZED_ENTITIES = {
    'CABO DA CRUZ': ['CABO DE CRUZ', 'CABO'],
    'ARES': ['DE ARES'],
    'CESANTES': ['CESANTES REMO - RODAVIGO'],
    'FEDERACION GALEGA DE REMO': ['LGT - FEGR'],
    'PERILLO': ['SALGADO PERILLO'],
    'LIGA GALEGA DE TRAIÑAS': ['LIGA GALEGA TRAIÑEIRAS', 'LIGA GALEGA TRAINEIRAS', 'LGT'],
    'BUEU': ['BUEU TECCARSA'],
    'ESTEIRANA': ['ESTEIRANA REMO'],
    'A CABANA': ['A CABANA FERROL'],
    'RIVEIRA': ['DE RIVEIRA'],
    'ZARAUTZ': ['ZARAUTZ GESALAGA-OKELAN', 'ZARAUTZ INMOB. ORIO'],
    'PASAI DONIBANE KOXTAPE': ['P.DONIBANE IBERDROLA'],
    'HONDARRIBIA': ['HONADRRIBIA', 'HONDARRBIA'],
    'SANTURTZI': ['ITSASOKO AMA', 'SOTERA'],
    'ONDARROA': ['OMDARROA'],
    'ILLUMBE': ['ILLUNBE'],
    'PORTUGALETE': ['POTUGALETE'],
    'GETXO': ['GETRXO'],
    'DONOSTIARRA': ['DNOSTIARRA'],
}


def normalize_club_name(name: str) -> str:
    name = whitespaces_clean(remove_parenthesis(name.upper()))
    name = remove_club_title(name)

    # specific club normalizations
    for k, v in __NORMALIZED_ENTITIES.items():
        if name in v or any(part in name for part in v):
            name = k
            break

    return whitespaces_clean(name)


def remove_club_title(name: str) -> str:
    name = ' '.join(w for w in name.split() if w not in __ENTITY_TITLES)
    return whitespaces_clean(name)
