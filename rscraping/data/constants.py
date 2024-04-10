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
SYNONYM_FEMALE = "FEMENINA"
SYNONYM_VETERAN = "VETERANO"
SYNONYM_FLAG = "BANDERA"
SYNONYM_GRAND_PRIX = "GRAN PREMIO"
SYNONYM_MEMORIAL = "MEMORIAL"
SYNONYM_CITY_HALL = "AYUNTAMIENTO"
SYNONYM_TIME_TRIAL = "CONTRARRELOJ"
SYNONYM_TRAINERA = "TRAINERA"
SYNONYM_RACE = "REGATA"
SYNONYM_DIPUTATION = "DIPUTACION"
SYNONYM_QUALIFYING = "CLASIFICATORIA"
SYNONYM_PORT = "PUERTO"
SYNONYM_BAY = "BAHIA"
SYNONYM_ROWER = "REMERO"
SYNONYM_COXWAIN = "PATRON"
SYNONYM_HOMEGROWN = "CANTERANO"
SYNONYM_OWN = "PROPIO"
SYNONYM_NOT_OWN = "NO PROPIO"
SYNONYM_COACH = "ENTRENADOR"
SYNONYM_DELEGATE = "DELEGADO"

SYNONYMS = {
    SYNONYM_FEMALE: [
        "FEMENINA",
        "FEMININA",
        "FEMENINO",
        "FEMININO",
        "FEMINAS",
        "EMAKUMEEN",
        "EMAKUMEAK",
        "NESKEN",
        "NESKA",
        "EMAKUMEZKOEN",
    ],
    SYNONYM_VETERAN: ["VETERANO", "VETERANA"],
    SYNONYM_FLAG: ["BANDERA", "BANDEIRA", "IKURRIÑA"],
    SYNONYM_GRAND_PRIX: ["GRAN PREMIO", "SARI NAGUSIA", "GRAND PRIX"],
    SYNONYM_MEMORIAL: ["MEMORIAL", "OMEALDIA"],
    SYNONYM_CITY_HALL: [
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
    SYNONYM_TIME_TRIAL: ["CONTRARRELOJ", "CONTRARRELOXO", "ERLOJUPEKOA", "ERLOJU KONTRA", "CONTRA RELOJ"],
    SYNONYM_TRAINERA: ["TRAINERA", "TRAINERAS", "TRAINERU", "TRAIÑA", "TRAIÑAS", "TRAIÑEIRA", "TRAIÑEIRAS"],
    SYNONYM_RACE: ["REGATA", "REGATAS", "ESTROPADA", "ESTROPADAK"],
    SYNONYM_DIPUTATION: ["DEPUTACIÓN", "DIPUTACIÓN", "DEPUTACION", "DIPUTACION"],
    SYNONYM_QUALIFYING: ["CLASIFICATORIA", "SAILKAPEN OROKORRA", "CLASIFICACION GENERAL", "ELIMINATORIA"],
    SYNONYM_PORT: ["PEIRAO COMERCIAL", "PUERTO", "PORTO", "PEIRAO", "MUELLE", "PRAIA"],
    SYNONYM_BAY: ["BAIA", "BAHIA"],
    SYNONYM_ROWER: ["REMERO", "REMERA", "REMEIRO", "REMEIRA", "REMEROS", "REMERAS", "REMEIRAS", "REMEIROS"],
    SYNONYM_COXWAIN: ["PATRON", "PATRÓN", "PATRONA", "PATROA"],
    SYNONYM_HOMEGROWN: ["CANTERANO", "CANTEIRAN", "CANTEIRÁN", "CANTERANA", "CANTEIRA", "CANTEIRÁ"],
    SYNONYM_OWN: ["PROPIO", "PROPIA", "PROPIOS", "PROPIAS"],
    SYNONYM_NOT_OWN: ["NO PROPIO", "NO PROPIA", "NON PROPIO", "NON PROPIA"],
    SYNONYM_COACH: ["ADESTRADOR", "ADESTRADORA", "ENTRENADOR", "ENTRENADORA"],
    SYNONYM_DELEGATE: ["DELEGADO", "DELEGADA"],
}
