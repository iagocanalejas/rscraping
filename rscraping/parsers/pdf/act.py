from typing import List, Optional, Tuple

from pypdf import PageObject
from pyutils.lists import flatten
from pyutils.strings import whitespaces_clean

from rscraping.data.constants import SYNONYMS
from rscraping.data.models import Datasource, Lineup
from rscraping.data.normalization.clubs import normalize_club_name
from rscraping.data.normalization.races import normalize_race_name

from ._parser import PdfParser


class ACTPdfParser(PdfParser):
    DATASOURCE = Datasource.ACT

    _TRASH = ["FIRMA Y SELLO", "PROPIOS:", "CANTERANOS:", "NO PROPIOS:", "CAPITÁN", "CAPITANA"]
    _CONDITION = list(flatten([SYNONYMS["HOMEGROWN"], SYNONYMS["OWN"], SYNONYMS["NOT_OWN"]]))

    def parse_lineup(self, page: PageObject) -> Optional[Lineup]:
        text = [e for e in page.extract_text().split("\n") if e]
        if len(text) == 0:
            return None

        split = text.index("Entrenador")
        race, club = self._parse_name(text[:split])
        coach, delegate, substitutes, rowers = self._parse_rowers(text[split:])
        return Lineup(
            race=race,
            club=club,
            coach=coach,
            delegate=delegate,
            coxswain=None,
            starboard=rowers,
            larboard=rowers,
            substitute=substitutes,
            bow=None,
        )

    @staticmethod
    def _parse_name(parts: List[str]) -> Tuple[str, str]:
        useful_part = [p for p in parts if "Club:" in p][0]
        race = useful_part.split("- Puntuable")[0].split("/")[1]
        club = useful_part.split("Club:")[1]
        return normalize_race_name(race), normalize_club_name(club)

    # TODO: find a way to retrieve 'coxswain', 'bow', 'starboard' and 'larboard'
    def _parse_rowers(self, rowers: List[str]) -> Tuple[str, str, List[str], List[str]]:
        rowers = [r for r in rowers if not any(t for t in self._TRASH if t in r.upper())]

        coach, delegate = self._get_coach_and_delegate(rowers)

        indexes = self._get_substitutes_tokens_indexes(rowers)
        substitutes = self._build_names_between_indexes(rowers, indexes)

        rowers = rowers[indexes[-1] - 1 :]  # remove substitutes
        indexes = [idx for idx, rower in enumerate(rowers) if rower.upper() in self._CONDITION]
        valid_rowers = self._build_names_between_indexes(rowers, indexes)

        return coach, delegate, substitutes, valid_rowers

    def _build_names_between_indexes(self, rowers: List[str], indexes: List[int]) -> List[str]:
        items = []
        for i in range(0, len(indexes) - 1):
            name_parts = rowers[indexes[i] + 1 : indexes[i + 1]]
            name_parts = [n for n in name_parts if n.upper() not in self._CONDITION]
            items.append(whitespaces_clean(" ".join(name_parts)))
        return items

    def _get_substitutes_tokens_indexes(self, rowers: List[str]) -> List[int]:
        def is_substitute_index(rower: str) -> bool:
            return rower.upper() in SYNONYMS["ROWER"] or rower.upper() in SYNONYMS["COXWAIN"]

        # ['Remero', 'EKAITZ ', 'BADIOLA', 'Canterano', 'Remero', 'UNAX ', 'BEDIALAUNETA', 'Canterano', ...]
        # find all substitutes (marked as 'Remero' | 'Patrón')
        indexes = [idx for idx, rower in enumerate(rowers) if is_substitute_index(rower)]

        # add next _CONDITION after the last found substitute to build the name ('Canterano')
        tail = rowers[indexes[-1] :]
        next_idx = next(i + 1 for i, x in enumerate(tail) if x.upper() in self._CONDITION)
        indexes.append(indexes[-1] + next_idx)

        return indexes

    def _get_coach_and_delegate(self, rowers: List[str]) -> Tuple[str, str]:
        # rowers are always sorted like ['Entrenador', 'IÑAKI', 'ERRASTI', 'Delegado', 'HASIER', 'Suplentes', ...]
        coach = whitespaces_clean(" ".join(rowers[rowers.index("Entrenador") + 1 : rowers.index("Delegado")]))
        delegate = whitespaces_clean(" ".join(rowers[rowers.index("Delegado") + 1 : rowers.index("Suplentes")]))
        return coach, delegate
