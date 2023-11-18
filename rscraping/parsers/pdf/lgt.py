import re

from fitz import Page

from pyutils.lists import flatten
from rscraping.data.constants import SYNONYMS
from rscraping.data.models import Datasource, Lineup
from rscraping.data.normalization.clubs import normalize_club_name
from rscraping.data.normalization.races import normalize_race_name

from ._parser import PdfParser


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

    def parse_lineup(self, page: Page) -> Lineup:
        text = [e for e in page.get_text().split("\n") if e]
        (race, club), rowers = self._parse_name(text[0]), self._parse_rowers(text[1:])
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
            images=[],
        )

    @staticmethod
    def _parse_name(name: str) -> tuple[str, str]:
        parts = name.split("-")
        return normalize_race_name(parts[0]), normalize_club_name(" ".join(parts[1:]))

    def _parse_rowers(self, rowers: list[str]) -> list[tuple[str, str]]:
        new_rowers = self._clean_rowers_list(rowers)

        # converts a list of ['DELEGADO', 'EMILIO JOSE', 'DIESTE REGADES', 'ADESTRADOR', 'MANUEL RAUL', 'PAZOS'] in
        # a list of tupples like [('DELEGADO', 'EMILIO JOSE DIESTE REGADES'), ('ADESTRADOR', 'MANUEL RAUL PAZOS')]
        valid_rowers = []
        indexes = [i for i, rower in enumerate(new_rowers) if any(e in rower for e in self._TOKEN)]
        for i in range(0, len(indexes) - 1):
            parts = new_rowers[indexes[i] : indexes[i + 1]]
            valid_rowers.append((parts[0], " ".join(parts[1:])))
        return sorted(valid_rowers, key=lambda x: x[0])

    def _clean_rowers_list(self, rowers: list[str]) -> list[str]:
        new_rowers = []
        for raw_name in rowers:
            if "Licenza" in raw_name:
                raw_name = re.sub(r"Licenza: (FRS|FRD|FRJ|FRT|FRV)?\d+", "", raw_name, flags=re.IGNORECASE)

            if raw_name and raw_name.upper() not in self._CONDITION:
                new_rowers.extend(self._split_token_from_name(raw_name))
        return new_rowers

    def _split_token_from_name(self, name: str) -> list[str]:
        # finds the 'SUPLENTE' in 'VÁZQUEZ PENASUPLENTE 2'
        match = next((t for t in self._TOKEN if t in name and not name.startswith(t)), None)
        if not match:
            return [name]

        # splits 'VÁZQUEZ PENASUPLENTE 2' in ['VÁZQUEZ PENA', 'SUPLENTE 2']
        parts = name.split(match)
        return [parts[0], match + parts[1]]
