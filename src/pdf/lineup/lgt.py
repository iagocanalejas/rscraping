import logging
import re
from typing import Tuple, List

from pypdf import PageObject

from ai_django.ai_core.utils.strings import whitespaces_clean

from src.pdf.lineup._lineup import LineupPdfParser
from src.utils.models import Datasource, LineUpItem

logger = logging.getLogger(__name__)


class LGTLineupPdfParser(LineupPdfParser, source=Datasource.LGT):
    DATASOURCE = Datasource.LGT

    _CONDITION = ["CANTEIRÁ", "CANTEIRÁN", "PROPIO", "PROPIA", "NON PROPIO", "NON PROPIA"]
    _TOKEN = ["DELEGADO", "DELEGADA", "ADESTRADOR", "ADESTRADORA", "ESTRIBOR", "BABOR", "PATRÓN", "PATROA", "PROEL", "SUPLENTE"]

    def parse_page(self, page: PageObject) -> LineUpItem:
        text = page.extract_text().split("\n")
        (race, club), rowers = self._parse_name(text[0]), self._clean_rowers(text[1:])
        return LineUpItem(
            race=race,
            club=club,
            coach=[r for t, r in rowers if t in ['ADESTRADOR', 'ADESTRADORA']][0],
            delegate=[r for t, r in rowers if t in ['DELEGADO', 'DELEGADA']][0],
            coxswain=[r for t, r in rowers if t in ['PATRÓN', 'PATRON', 'PATROA']][0],
            starboard=[r for t, r in rowers if any(k in t for k in ['ESTRIBOR'])],
            larboard=[r for t, r in rowers if any(k in t for k in ['BABOR'])],
            substitute=[r for t, r in rowers if any(k in t for k in ['SUPLENTE'])],
            bow=[r for t, r in rowers if t in ['PROEL']][0],
        )

    @staticmethod
    def _parse_name(name: str) -> Tuple[str, str]:
        parts = name.split('-')
        return whitespaces_clean(parts[0]).upper(), whitespaces_clean(' '.join(parts[1:])).upper()

    def _clean_rowers(self, rowers: List[str]) -> List[Tuple[str, str]]:
        new_rowers = []
        for raw_name in rowers:
            if 'Licenza' in raw_name:
                raw_name = re.sub(r'Licenza: (FRS|FRD|FRJ|FRT|FRV)?\d+', '', raw_name, flags=re.IGNORECASE)

            if raw_name and raw_name.upper() not in self._CONDITION:
                match = next((t for t in self._TOKEN if t in raw_name and not raw_name.startswith(t)), None)
                if not match:
                    new_rowers.append(raw_name.upper())
                    continue

                # split 'VÁZQUEZ PENASUPLENTE 2' into ['VÁZQUEZ PENA', 'SUPLENTE 2']
                parts = raw_name.split(match)
                rower, extra = parts[0], match + parts[1]
                new_rowers.extend([rower.upper(), extra.upper()])

        valid_rowers = []
        indexes = [i for i, rower in enumerate(new_rowers) if any(e in rower for e in self._TOKEN)]
        for i in range(1, len(indexes)):
            parts = new_rowers[indexes[i-1]:indexes[i]]
            valid_rowers.append((parts[0], ' '.join(parts[1:])))
        return sorted(valid_rowers, key=lambda x: x[0])
