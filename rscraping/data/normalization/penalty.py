import re
from collections.abc import Generator

from pyutils.strings import find_time, remove_parenthesis
from rscraping.data.constants import (
    BOAT_WEIGHT_LIMIT,
    COLLISION,
    COXWAIN_WEIGHT_LIMIT,
    LACK_OF_COMPETITIVENESS,
    NO_LINE_START,
    NULL_START,
    OFF_THE_FIELD,
    SINKING,
    STARBOARD_TACK,
    WRONG_LINEUP,
    WRONG_ROUTE,
)
from rscraping.data.models import Penalty, PenaltyDict

from .clubs import normalize_club_name
from .lemmatize import lemmatize

_LEMMAS = {
    BOAT_WEIGHT_LIMIT: [["pesar", "embarcacion"]],
    COLLISION: [
        ["abordar"],
        ["demasiado", "abrir"],
        ["delante"],
        ["estorbo"],
        ["molesto"],
        ["invasion"],
        ["invadir"],
        ["chocar"],
    ],
    COXWAIN_WEIGHT_LIMIT: [],
    LACK_OF_COMPETITIVENESS: [["falto", "voluntad", "competir"]],
    NO_LINE_START: [],
    NULL_START: [["nulo", "salida"], ["tarde", "salida"]],
    OFF_THE_FIELD: [["estribor", "meta"], ["meta", "entrar"]],
    SINKING: [["hundio"]],
    STARBOARD_TACK: [["estribor", "ciaboga"]],
    WRONG_LINEUP: [["ficha", "remero"], ["alineacion", "indebido"]],
    WRONG_ROUTE: [],
}

_TEMPLATES = {
    BOAT_WEIGHT_LIMIT: [
        r"(.*) fue descalificado por no pesar la embarcación",
    ],
    COLLISION: [
        r"(.*) salió (demasiado|muy) abiert(o|a)",
        r".* fue abordado por (.*) en .*",
        r"(.*) se puso delante de .*",
        r"(.*) fue descalificado por ponerse delante de .*",
        r"(.*) estorbó a .* en la .*",
        r"(.*) pero fue descalificada por invasión .*",
        r".* jornada (.*) fue descalificado por invadir .*",
        r"(.*) se chocó .*",
    ],
    COXWAIN_WEIGHT_LIMIT: [],
    LACK_OF_COMPETITIVENESS: [
        r"Se consideró que a (.*) le faltó voluntad de competir.*",
    ],
    NO_LINE_START: [],
    NULL_START: [
        r"(.*) tuvo .* salida(s)? nula(s)?",
        r"(.*) compitió fuera de regata por salida(s)? nula(s)?",
        r"(.*) quedó fuera .* tarde a la salida",
    ],
    OFF_THE_FIELD: [
        r"(.*) entró a meta fuera de linea.*",
        r"(.*) (pas(ó|aron)|dej(ó|aron)) la baliza de meta por estribor",
        r"(.*) fue descalificad(o|a) por entrar en meta dejando la boya por estribor",
        r"(.*) fue descalificad(o|a) por dejar por estribor una baliza .* meta",
        r"(.*) pero fue descalificado por dejar su baliza por estribor a la entrada a meta",
        r"(.*) entró a meta fuera de línea",
    ],
    SINKING: [
        r"(.*) se hundió .*",
    ],
    STARBOARD_TACK: [
        r"(.*) realiz(i)?ó (la primera|una) ciaboga por estribor",
        r"(.*) fue descalificado por dejar por estribor una baliza .*",
    ],
    WRONG_LINEUP: [
        r"(.*) quedó fuera de regata (por alineación indebida|después de una reclamación por problemas con) .*",
    ],
    WRONG_ROUTE: [],
}

_CANCELLED = [
    "se suspendió",
    "tanda no salió",
    "anular la regata",
    "regata se anuló",
    "fue anulada",
]


def is_cancelled(text: str | None) -> bool:
    """
    Check if a text contains any of the known patterns for a cancelled race
    """
    return text is not None and any(w in text for w in _CANCELLED)


def normalize_penalty(text: str | None) -> PenaltyDict:
    """
    Retrieve a dict of penalties in the format {club_name: (time, penalty)} from a text.

    1. Normalize the text by replacing known common patters.
    2. Split the text by "." as penalties use to be separated by a colon.
    3. For each note, check if it is a time note or a penalty note.
    4. If it is a time note, add the time to the penalties dict.
    5. If it is a penalty note, check if it matches any of the known penalty templates.
    6. If it matches, retrieve the club name and add the penalty to the penalties dict.
    """

    penalties: PenaltyDict = {}
    if not text:
        return penalties

    text = text.replace(", el de", ". El tiempo de").replace("y el de", ". El tiempo de")  # normalize time notes
    notes = text.split(". ")

    for note in notes:
        if note.endswith("."):
            note = note[:-1]

        if "El tiempo" in note:
            # note that just provides a club time without any other information
            penalties, new_note = _process_time_note(note, penalties)
            if new_note:
                notes.append(new_note)
            continue

        if any(w in note.lower() for w in ["su tiempo", "un tiempo de"]):
            # note that provides a club time for an existing penalty
            match = re.match(r"(.*) fue descalificado.* había sido de (.*)", note, flags=re.IGNORECASE | re.UNICODE)
            if not match:
                time = find_time(note)
                if time:
                    penalties = Penalty.push(penalties, time=time.strftime("%M:%S.%f"))
                continue

            if len(match.groups()) != 2:
                continue

            club_name, maybe_time = match.groups()
            time = find_time(maybe_time)
            if time:
                penalties = Penalty.push(penalties, club_name.upper(), time.strftime("%M:%S.%f"))
            continue

        note_lemmas = lemmatize(remove_parenthesis(note))
        for penalty_str, lemmas in _LEMMAS.items():
            for word in lemmas:
                if not all(lemma in note_lemmas for lemma in word):
                    continue
                for name in _retrieve_club_names(note, penalty_str):
                    penalty = Penalty(reason=penalty_str, disqualification=True)
                    penalties = Penalty.push(penalties, name, penalty=penalty)
                break

    return penalties


def _process_time_note(note: str, penalties: PenaltyDict) -> tuple[PenaltyDict, str | None]:
    new_note = None
    clean_note = (
        note.replace("El tiempo del ", "")
        .replace("El tiempo de ", "")
        .replace(" había sido de ", ", ")
        .replace(" había sido ", ", ")
    )
    clean_note = re.sub(r" de ([\d:.]+)", r", \1", clean_note)
    parts = clean_note.split(", ")

    if len(parts) > 2:
        club_name, time = parts[0], parts[1]
        extra = parts[2:]
        parts = [club_name, time]
        new_note = f"{club_name} {' '.join(extra)}"

    if len(parts) != 2:
        return penalties, new_note

    club_name, time = normalize_club_name(parts[0].upper()), find_time(parts[1])
    if time:
        penalties = Penalty.push(penalties, club_name, time.strftime("%M:%S.%f"))

    return penalties, new_note


def _retrieve_club_names(note: str, penalty: str) -> Generator[str, None, None]:
    club_name = None
    for r in _TEMPLATES[penalty]:
        match = re.match(r, note, flags=re.IGNORECASE | re.UNICODE)
        if match:
            club_name = match.group(1)
            break
    if club_name:
        yield from normalize_club_name(club_name.upper()).replace(" Y EL ", " Y ").split(" Y ")
