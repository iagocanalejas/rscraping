import re
from datetime import time

from pyutils.strings import find_time, lstrip_conjunctions, remove_parenthesis
from rscraping.data.constants import (
    BOAT_WEIGHT_LIMIT,
    COLLISION,
    COXWAIN_WEIGHT_LIMIT,
    DOPING,
    LACK_OF_COMPETITIVENESS,
    NO_LINE_START,
    NULL_START,
    OFF_THE_FIELD,
    SINKING,
    STARBOARD_TACK,
    WRONG_LINEUP,
    WRONG_ROUTE,
)
from rscraping.data.models import Penalty

from .clubs import normalize_club_name
from .lemmatize import lemmatize

_CANCELLED_LEMMAS = [
    ["anular", "regata"],
    ["cancelar", "regata"],
    ["suspender", "regata"],
    ["anular", "prueba"],
    ["cancelar", "prueba"],
    ["suspender", "prueba"],
    ["tanda", "no", "salir"],
]


def is_cancelled(note: str | None) -> bool:
    if not note:
        return False

    lemmas = lemmatize(remove_parenthesis(note))
    return any(set(w).issubset(lemmas) for w in _CANCELLED_LEMMAS)


_RETIRED_RE = [
    r"(.*) abandonó.*",
    r"(.*) se retiró por.*",
    r"(.*) no tomó la salida por.*",
    r"(?:.*, )(.*) no quiso participar y se retiró.*",
]


def is_retired(participant: str, note: str | None) -> bool:
    if not note:
        return False
    found = _find_participant(note, _RETIRED_RE)
    if not found or participant not in found:
        return any(_find_participant(part, _RETIRED_RE) == participant for part in _clean_note(note))
    return True


_GUEST_RE = [
    r"(.*) (?:formaban?|participaban?).*promoción.*",
    r"(?:.*que)?(.*) no puntuaban",
]


def is_guest(participant: str, note: str | None) -> bool:
    if not note:
        return False
    found = _find_participant(note, _GUEST_RE)
    if not found or participant not in found:
        return any(_find_participant(part, _GUEST_RE) == participant for part in _clean_note(note))
    return True


_ABSENT_RE = [r"(?:.*de )(.*) pero no se presentó"]


def is_absent(participant: str, note: str | None) -> bool:
    if not note:
        return False
    found = _find_participant(note, _ABSENT_RE)
    if not found or participant not in found:
        return any(_find_participant(part, _ABSENT_RE) == participant for part in _clean_note(note))
    return True


_TIME_RE = [
    r"(.*) (?:tuvo|hizo|había realizado|marcó|realizó) un tiempo de ([\d:.,]+)",
    r"El tiempo(?: final)? de (.*) fue de ([\d:.,]+)",
    r"El tiempo(?: final)? de (.*) había sido(?: de)? ([\d:.,]+)",
    r"(?:y )?(?:mientras )?(?:el )?(?:de|del|que) (.*) fue (?:de|hizo) ([\d:.,]+)",
    r"(?:y )?(?:mientras )?(?:el )?(?:de|del|que) (.*) (?:de|hizo) ([\d:.,]+)",
    # -- no participant cases --
    r"(.*)Su tiempo(?: final)? (?:había sido|fue)(?: .*)? ([\d:.,]+)",
    r"(.*)Perdió.*realizar un tiempo de ([\d:.,]+)",
    r"(.*)Terminó con un tiempo de ([\d:.,]+)",
    r"(.*)Había realizado un tiempo de ([\d:.,]+)",
    r"(.*)siendo su tiempo(?: de)? ([\d:.,]+)",
    r"(.*)El tiempo fue de ([\d:.,]+)",
    # -- last case --
    r"(.*) de ([\d:.,]+)",
]


def retrieve_penalty_times(note: str) -> dict[str, time]:
    """
    Retrieve the participants and their times from a penalty

    1. Handle some weird cases that retrieves a list of participants and a list of times.
    2. Split the note into parts.
    3. For each part, try to find a participant and a time.
    """
    times: dict[str, time | None] = {}

    # weird cases with a list of participants and then a list of times
    r = r"(.*) formaban.*tiempos fueron(?: de) (.*)(?:,)(?: respectivamente)"
    match = re.match(r, note, flags=re.IGNORECASE | re.UNICODE)
    if match:
        participants = [normalize_club_name(p) for p in match.group(1).replace(" y ", ", ").split(",")]
        times = {p: find_time(t) for p, t in zip(participants, match.group(2).replace(" y ", ", ").split(","))}
        return {k: v for k, v in times.items() if v}

    parts = _clean_note(note)
    for part in parts:
        for r in _TIME_RE:
            match = re.match(r, part, flags=re.IGNORECASE | re.UNICODE)
            if match:
                participant = normalize_club_name(match.group(1).upper())
                assert participant not in times.keys(), f"participant {participant} already has a time"
                ttime = find_time(match.group(2))
                times[participant] = ttime
                break

    return {k: v for k, v in times.items() if v}


_LEMMAS = {
    BOAT_WEIGHT_LIMIT: [["pesar", "embarcacion"]],
    COLLISION: [
        ["abrir", "demasiado"],
        ["abrir", "molesto"],
        ["poner", "delante"],
        ["ponerse", "delante"],
        ["salir", "abrir"],
        ["abordaje"],
        ["abordar"],
        ["abordo"],
        ["chocar"],
        ["colisionar"],
        ["estorbo"],
        ["estorbar"],
        ["invasion"],
        ["invadir"],
        ["irrumpir"],
        ["molestar"],
        ["molesto"],
    ],
    COXWAIN_WEIGHT_LIMIT: [],
    DOPING: [["antidoping"], ["doping"], ["positivo"]],
    LACK_OF_COMPETITIVENESS: [["faltar", "voluntad", "competir"]],
    NO_LINE_START: [],
    NULL_START: [["nulo", "salida"], ["tarde", "salida"], ["deber", "baliza", "salir"]],
    SINKING: [["hundir"], ["entrar", "agua"]],
    WRONG_LINEUP: [["ficha", "remero"], ["remero", "licencia"], ["alineacion", "indebido"], ["juvenil"]],
}

_ROUTE_LEMMAS = [
    ["estribor", "meta"],
    ["estribor", "ciaboga"],
    ["estribor", "baliza"],
    ["entrar", "baliza"],
    ["ciaboga", "incorrecto"],
    ["meta", "entrar"],
    ["cruzarse", "calle"],
    ["dejar", "equivocar"],
]


_TEMPLATES = {
    BOAT_WEIGHT_LIMIT: [
        r"(.*) fue descalificado por no pesar la embarcación",
    ],
    COLLISION: [
        r".*jornada (.*) fue.*invadir.*",
        r".*fue abordado por (.*)",
        r"(.*) salió( demasiado| muy)? abiert(o|a).*",
        r"(.*) se puso delante.*",
        r"(.*) fue.*ponerse delante.*",
        r"(.*) fue.*(irrumpir|abordar|invadir|abordaje).*",
        r"(.*) (estorbó|se chocó|colisionó).*",
        r"(.*) se retiró.*colisionar.*",
        r".*jornada,? (.*) había.*abordó.*",  # this is too specific
    ],
    COXWAIN_WEIGHT_LIMIT: [],
    DOPING: [
        r"(.*) pero.*no pasó el control antidoping.*",
    ],
    LACK_OF_COMPETITIVENESS: [
        r"Se consideró que a (.*) le faltó voluntad de competir.*",
    ],
    NO_LINE_START: [],
    NULL_START: [
        r"(.*) tuvo.*salida(s)? nula(s)?",
        r"(.*) compitió fuera de regata por salida(s)? nula(s)?",
        r"(.*) quedó fuera.*tarde a la salida",
        r"(.*) debería.*baliza de salida.*",
    ],
    SINKING: [
        r"(.*) se hundió.*",
        r"(.*) se retiró por entrar agua .*",
    ],
    WRONG_LINEUP: [
        r"(.*) quedó fuera de regata (por alineación indebida|después de una reclamación por problemas con).*",
        "(.*) fue descalificado por llevar un remero.*",
        "(.*) fue descalificado por llevar juveniles",
        "(.*) fue descalificado por .*indebida",
        "(.*) ganó.*remeros con ficha.*",
    ],
}

_ROUTE_TEMPLATES = {
    OFF_THE_FIELD: [
        r"(.*) entró a meta fuera de linea.*",
        r"(.*) (pas(ó|aron)|dej(ó|aron)) la baliza de meta por estribor",
        r"(.*) ?pero.*descalificado.*baliza.*estribor.*meta",
        r"(.*) fue descalificad(o|a) por entrar en meta.*estribor",
        r"(.*) fue descalificad(o|a) por entrar en la baliza.*",
        r"(.*) fue descalificad(o|a) por dejar por estribor.*meta",
        r"(.*) fue descalificad(o|a) por dejar.*equivocado",
        r"(.*) entró.*meta.*fuera.*",
    ],
    STARBOARD_TACK: [
        r"(.*) ocupó.*fue descalificado por realizar la.*por estribor",
        r"(.*) (:?realiz(i)?ó|tomó|fue descalificad(o|a)|tuvo que).*(:? ciaboga|baliza).*(estribor|incorrecta)(?!.*meta).*",  # noqa: E501
        r"(.*) había dado.*estribor",
    ],
    WRONG_ROUTE: [
        r"(.*) fue descalificado por dejar por estribor una baliza.*recorrido.*",
        r"(.*) fue descalificado por cruzar.*calle",
    ],
}

_DISQUALIFICATION_LEMMAS = ["DESCALIFICADO", "DESCALIFICADA"]
_UNKNOWN_PENALTY_TEMPLATES = [
    "(.*) fue descalificado.*",
]


def normalize_penalty(text: str | None, participants: list[str]) -> dict[str, Penalty]:
    """
    Normalize a penalty note

    1. Retrieve the times of the participants.
    2. Recontextualize the note.
    3. Try to find the penalties in note parts.
    4. If no penalty is found, try to find the penalties in the whole note.
    5. If no penalty is found, try to find a disqualification.
    6. If no penalty is found, try to find an unknown penalty.
    """

    penalties: dict[str, Penalty] = {}
    if not text:
        return penalties

    og_text = "" + text
    times = retrieve_penalty_times(og_text)
    time_participant = list(times.keys())[0] if len(times) == 1 else None
    text = _recontextualize_note(text.upper(), participants)
    parts = _clean_note(text)

    def assign_penalty(
        text: str, text_lemmas: list[str], penalty_str: str, regexes: list[str]
    ) -> tuple[str, Penalty] | None:
        club_name = _find_participant(text, regexes)
        if (not club_name or club_name not in participants) and time_participant:
            club_name = time_participant
        if club_name and club_name in participants:
            assert club_name not in penalties.keys(), f"club {club_name} already has a penalty"
            # TODO: improve disqualification detection
            if penalty_str in [OFF_THE_FIELD, STARBOARD_TACK, WRONG_ROUTE]:
                disqualification = any(w in text for w in _DISQUALIFICATION_LEMMAS)
            else:
                disqualification = penalty_str not in [SINKING] and all(w not in text_lemmas for w in ["RETIRO"])
            disqualification = disqualification or penalty_str == OFF_THE_FIELD
            return club_name, Penalty(reason=penalty_str, disqualification=disqualification)

    for part in parts:  # parts_loop
        note_lemmas = lemmatize(remove_parenthesis(part))
        penalty_found = False

        # route penalties
        for lemmas_lists in _ROUTE_LEMMAS:  # lemmas_loop
            if not set(lemmas_lists).issubset(note_lemmas):
                continue  # lemmas_loop

            for penalty_str, regexes in _ROUTE_TEMPLATES.items():  # penalties_loop
                penalty = assign_penalty(part, note_lemmas, penalty_str, regexes)
                if penalty:
                    club_name, penalty = penalty
                    penalties[club_name] = penalty
                    penalty_found = True
                    break  # penalties_loop

            if penalty_found:
                break  # lemmas_loop

        if penalty_found:
            continue  # parts_loop

        # rest of the penalties
        for penalty_str, lemmas_lists in _LEMMAS.items():  # penalties_loop
            for lemmas in lemmas_lists:  # lemmas_loop
                if not set(lemmas).issubset(note_lemmas):
                    continue  # lemmas_loop

                penalty = assign_penalty(part, note_lemmas, penalty_str, _TEMPLATES[penalty_str])
                if penalty:
                    club_name, penalty = penalty
                    penalties[club_name] = penalty
                    penalty_found = True
                    break  # lemmas_loop

            if penalty_found:
                break  # penalties_loop

    if len(penalties.keys()) > 0:
        return penalties

    note_lemmas = lemmatize(remove_parenthesis(og_text))
    for penalty_str, lemmas_lists in _LEMMAS.items():  # penalties_loop
        penalty_found = False
        for lemmas in lemmas_lists:  # lemmas_loop
            if not set(lemmas).issubset(note_lemmas):
                continue  # lemmas_loop

            penalty = assign_penalty(og_text, note_lemmas, penalty_str, _TEMPLATES[penalty_str])
            if penalty:
                club_name, penalty = penalty
                penalties[club_name] = penalty
                penalty_found = True
                break  # lemmas_loop
        if penalty_found:
            break  # penalties_loop

    if time_participant and "fue descalificado" in og_text:
        club_name = time_participant
        assert club_name not in penalties.keys(), f"club {club_name} already has a penalty"
        penalties[club_name] = Penalty(reason=None, disqualification=True)

    if len(penalties.keys()) > 0:
        return penalties

    for regex in _UNKNOWN_PENALTY_TEMPLATES:
        match = re.match(regex, og_text, flags=re.IGNORECASE | re.UNICODE)
        if match:
            club_name = normalize_club_name(match.group(1).upper())
            assert club_name not in penalties.keys(), f"club {club_name} already has a penalty"
            penalties[club_name] = Penalty(reason=None, disqualification=True)
            break

    return penalties


def _clean_note(note: str | None) -> list[str]:
    if not note:
        return []
    note = note.replace(" y ", ", ").replace(". ", ", ").replace(" ue ", " fue ").rstrip(".")
    return [p.strip() for p in note.split(", ")]


def _find_participant(note: str, regex: list[str]) -> str | None:
    for r in regex:
        match = re.match(r, note, flags=re.IGNORECASE | re.UNICODE)
        if match:
            return normalize_club_name(match.group(1).upper())
    return None


def _recontextualize_note(text: str, participants: list[str]) -> str:
    if " Y " in text:
        new_text = ""
        for part in text.split(". "):
            if part.count(" Y ") != 1:
                new_text += part + ". "
                continue

            parts = part.split(" Y ")
            clean_part = lstrip_conjunctions(parts[1])
            for p in participants:
                clean_part = clean_part.replace(p.upper(), "")
            clean_part = clean_part.strip()

            new_text += parts[0] + " " + clean_part + ". "
            new_text += parts[1] + ". "
        return new_text.strip()
    return text
