from typing import Optional, Tuple, List

from pypdf import PageObject

from ai_django.ai_core.utils.strings import whitespaces_clean
from src.pdf.lineup import LineUpParser
from src.utils.models import Datasource, LineUpItem


class ACTLineUpParser(LineUpParser, source=Datasource.ACT):
    DATASOURCE = Datasource.ACT

    _TRASH = ["FIRMA Y SELLO", "PROPIOS:", "CANTERANOS:", "NO PROPIOS:", "CAPITÁN"]
    _CONDITION = ["CANTERANO", "CANTERANA", "PROPIO", "PROPIA", "NO PROPIO", "NO PROPIA"]

    def parse_page(self, page: PageObject) -> Optional[LineUpItem]:
        text = [e for e in page.extract_text().split("\n") if e]
        if len(text) == 0:
            return None

        split = text.index('Entrenador')
        race, club = self._parse_name(text[:split])
        coach, delegate, substitutes, rowers = self._clean_rowers(text[split:])
        return LineUpItem(
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
        useful_part = [p for p in parts if 'Club:' in p][0]
        race = useful_part.split('- Puntuable')[0].split('/')[1]
        club = useful_part.split('Club:')[1]
        return whitespaces_clean(race).upper(), whitespaces_clean(club).upper()

    # TODO: find a way to retrieve 'coxswain', 'bow', 'starboard' and 'larboard'
    def _clean_rowers(self, rowers: List[str]) -> Tuple[str, str, List[str], List[str]]:
        rowers = [r for r in rowers if not any(t for t in self._TRASH if t in r.upper())]
        coach = whitespaces_clean(" ".join(rowers[rowers.index('Entrenador') + 1:rowers.index('Delegado')]))
        delegate = whitespaces_clean(" ".join(rowers[rowers.index('Delegado') + 1:rowers.index('Suplentes')]))
        substitutes = []

        # find all substitutes (marked as 'Remero' | 'Patrón')
        indexes = [i for i, rower in enumerate(rowers) if rower == 'Remero' or rower == 'Patrón']
        # add next _CONDITION after the last found substitute to build the name
        indexes.append(next(indexes[-1] + i + 1 for i, x in enumerate(rowers[indexes[-1]:]) if x.upper() in self._CONDITION))
        for i in range(1, len(indexes)):
            # discard range marks from the name building
            name_parts = rowers[indexes[i - 1] + 1:indexes[i] - 1]
            substitutes.append(whitespaces_clean(' '.join(name_parts)))

        valid_rowers = []
        rowers = rowers[indexes[-1] - 1:]  # remove substitutes
        indexes = [i for i, rower in enumerate(rowers) if rower.upper() in self._CONDITION]
        for i in range(1, len(indexes)):
            parts = rowers[indexes[i - 1] + 1:indexes[i]]
            valid_rowers.append(whitespaces_clean(' '.join(parts)))
        return coach, delegate, substitutes, valid_rowers
