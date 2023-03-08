import logging
import re
from typing import List, Tuple

from pypdf import PageObject
from pyutils.lists import flatten
from pyutils.strings import whitespaces_clean

from rscraping.data.constants import SYNONYMS
from rscraping.data.models import Datasource, Lineup

from ._parser import PdfParser

logger = logging.getLogger(__name__)


class LGTPdfParser(PdfParser):
    DATASOURCE = Datasource.LGT

    _CONDITION = list(flatten([SYNONYMS["HOMEGROWN"], SYNONYMS["OWN"], SYNONYMS["NOT_OWN"]]))
    _TOKEN = list(
        flatten(
            [
                SYNONYMS["COACH"],
                SYNONYMS["DELEGATE"],
                SYNONYMS["COXWAIN"],
                ["ESTRIBOR", "BABOR", "PROEL", "SUPLENTE"],
            ]
        )
    )

    def parse_lineup(self, page: PageObject) -> Lineup:
        text = page.extract_text().split("\n")
        (race, club), rowers = self._parse_name(text[0]), self._clean_rowers(text[1:])
        return Lineup(
            race=race,
            club=club,
            coach=[r for t, r in rowers if t in SYNONYMS["COACH"]][0],
            delegate=[r for t, r in rowers if t in SYNONYMS["DELEGATE"]][0],
            coxswain=[r for t, r in rowers if t in SYNONYMS["COXWAIN"]][0],
            starboard=[r for t, r in rowers if any(k in t for k in ["ESTRIBOR"])],
            larboard=[r for t, r in rowers if any(k in t for k in ["BABOR"])],
            substitute=[r for t, r in rowers if any(k in t for k in ["SUPLENTE"])],
            bow=[r for t, r in rowers if t in ["PROEL"]][0],
        )

    @staticmethod
    def _parse_name(name: str) -> Tuple[str, str]:
        parts = name.split("-")
        return whitespaces_clean(parts[0]).upper(), whitespaces_clean(" ".join(parts[1:])).upper()

    def _clean_rowers(self, rowers: List[str]) -> List[Tuple[str, str]]:
        new_rowers = []
        for raw_name in rowers:
            if "Licenza" in raw_name:
                raw_name = re.sub(r"Licenza: (FRS|FRD|FRJ|FRT|FRV)?\d+", "", raw_name, flags=re.IGNORECASE)

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
            parts = new_rowers[indexes[i - 1] : indexes[i]]
            valid_rowers.append((parts[0], " ".join(parts[1:])))
        return sorted(valid_rowers, key=lambda x: x[0])
