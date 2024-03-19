import random

################
#   RACE TYPE  #
################
RACE_CONVENTIONAL = "CONVENTIONAL"
RACE_TIME_TRIAL = "TIME_TRIAL"

################
#  MODALITIES  #
################
RACE_TRAINERA = "TRAINERA"
RACE_TRAINERILLA = "TRAINERILLA"
RACE_BATEL = "BATEL"

################
#  CATEGORIES  #
################
CATEGORY_ABSOLUT = "ABSOLUT"
CATEGORY_VETERAN = "VETERAN"
CATEGORY_SCHOOL = "SCHOOL"

################
#   ENTITIES   #
################
ENTITY_CLUB = "CLUB"
ENTITY_LEAGUE = "LEAGUE"
ENTITY_FEDERATION = "FEDERATION"
ENTITY_PRIVATE = "PRIVATE"

################
#   GENDERS    #
################
GENDER_ALL = "ALL"
GENDER_MALE = "MALE"
GENDER_FEMALE = "FEMALE"
GENDER_MIX = "MIX"

################
#  PENALTIES   #
################
NO_LINE_START = "NO_LINE_START"
NULL_START = "NULL_START"
BLADE_TOUCH = "BLADE_TOUCH"


################
# OTHER THINGS #
################
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/54.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/16.16299",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",  # noqa
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/60.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6",  # noqa
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/60.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.18362",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",  # noqa
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/70.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/75.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",  # noqa
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",  # noqa
]


def HTTP_HEADERS():
    return {
        "Accept": "*/*",
        "User-Agent": _USER_AGENTS[random.randint(0, len(_USER_AGENTS) - 1)],
    }


################
#   SYNONYMS   #
################
SYNONYMS = {
    "FEMENINA": ["FEMENINA", "FEMININA", "FEMINAS", "EMAKUMEEN", "EMAKUMEAK", "NESKEN", "NESKA", "EMAKUMEZKOEN"],
    "BANDERA": ["BANDERA", "BANDEIRA", "IKURRIÑA"],
    "GRAN PREMIO": ["GRAN PREMIO", "SARI NAGUSIA", "GRAND PRIX"],
    "AYUNTAMIENTO": [
        "AYUNTAMIENTO",
        "CONCELLO",
        "CONCEJO",
        "UDALETXEA",
        "UDALA",
        "VILA",
        "VILLA",
        "CIUDAD",
        "HIRIA",
        "HIRIKO",
        "CIDADE",
        "UDALAREN",
    ],
    "CONTRARRELOJ": ["CONTRARRELOJ", "CONTRARRELOXO", "ERLOJUPEKOA", "ERLOJU KONTRA", "CONTRA RELOJ"],
    "TRAINERA": ["TRAINERA", "TRAINERAS", "TRAINERU", "TRAIÑA", "TRAIÑAS", "TRAIÑEIRA", "TRAIÑEIRAS"],
    "REGATA": ["REGATA", "REGATAS", "ESTROPADA", "ESTROPADAK"],
    "DIPUTACION": ["DEPUTACIÓN", "DIPUTACIÓN", "DEPUTACION", "DIPUTACION"],
    "CLASIFICATORIA": ["SAILKAPEN OROKORRA", "CLASIFICACION GENERAL", "ELIMINATORIA"],
    "PUERTO": ["PEIRAO COMERCIAL", "PUERTO", "PORTO", "PEIRAO", "MUELLE", "PRAIA"],
    "ROWER": ["REMERO", "REMERA"],
    "COXWAIN": ["PATRON", "PATRÓN", "PATRONA", "PATROA"],
    "HOMEGROWN": ["CANTERANO", "CANTEIRAN", "CANTEIRÁN", "CANTERANA", "CANTEIRA", "CANTEIRÁ"],
    "OWN": ["PROPIO", "PROPIA"],
    "NOT_OWN": ["NO PROPIO", "NO PROPIA", "NON PROPIO", "NON PROPIA"],
    "COACH": ["ADESTRADOR", "ADESTRADORA"],
    "DELEGATE": ["DELEGADO", "DELEGADA"],
}
