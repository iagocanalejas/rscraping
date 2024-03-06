import sys

from fitz import Page

from pyutils.lists import flatten
from pyutils.strings import whitespaces_clean
from rscraping.data.constants import SYNONYMS
from rscraping.data.models import Datasource, Lineup
from rscraping.data.normalization.clubs import normalize_club_name
from rscraping.data.normalization.races import normalize_race_name

from ._protocol import PdfParser


class ACTPdfParser(PdfParser):
    DATASOURCE = Datasource.ACT

    _TRASH = ["FIRMA Y SELLO", "PROPIOS:", "CANTERANOS:", "NO PROPIOS:", "CAPITÁN", "CAPITANA"]
    _CONDITION = list(flatten([SYNONYMS["HOMEGROWN"], SYNONYMS["OWN"], SYNONYMS["NOT_OWN"]]))

    def parse_lineup(self, page: Page) -> Lineup | None:
        text = [e for e in page.get_text().split("\n") if e]
        if len(text) == 0:
            return None

        split = text.index("Entrenador")
        race, club = self._parse_name(text[:split])
        coach, delegate, substitutes, rowers = self._parse_rowers(text[split:])

        coxswain, bow = self._get_coxswain_and_bow(page, rowers)
        rowers = [r for r in rowers if r != coxswain and r != bow]
        starboard, lardboard = self._get_starboard_and_lardboard(page, rowers)

        return Lineup(
            race=race,
            club=club,
            coach=coach,
            delegate=delegate,
            coxswain=coxswain,
            starboard=starboard,
            larboard=lardboard,
            substitute=substitutes,
            bow=bow,
            images=[],
        )

    @staticmethod
    def _parse_name(parts: list[str]) -> tuple[str, str]:
        race_part = next(e for e in parts if "Puntuable" in e)
        club_index = next(idx for idx, value in enumerate(parts) if "Puntos" in value) + 2
        race = race_part.split("- Puntuable")[0].split("/")[1]
        club = parts[club_index]
        return normalize_race_name(race), normalize_club_name(club)

    def _parse_rowers(self, rowers: list[str]) -> tuple[str, str, list[str], list[str]]:
        rowers = [r for r in rowers if not any(t for t in self._TRASH if t in r.upper())]

        coach, delegate = self._get_coach_and_delegate(rowers)

        indexes = self._get_substitutes_tokens_indexes(rowers)
        substitutes = self._build_names_between_indexes(rowers, indexes)

        rowers = rowers[indexes[-1] - 1 :]  # remove substitutes
        indexes = [idx for idx, rower in enumerate(rowers) if rower.upper() in self._CONDITION]
        valid_rowers = self._build_names_between_indexes(rowers, indexes)

        return coach, delegate, substitutes, valid_rowers

    def _build_names_between_indexes(self, rowers: list[str], indexes: list[int]) -> list[str]:
        items = []
        for i in range(0, len(indexes) - 1):
            name_parts = rowers[indexes[i] + 1 : indexes[i + 1]]
            name_parts = [n for n in name_parts if n.upper() not in self._CONDITION]
            items.append(whitespaces_clean(" ".join(name_parts)))
        return items

    def _get_substitutes_tokens_indexes(self, rowers: list[str]) -> list[int]:
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

    def _get_coach_and_delegate(self, rowers: list[str]) -> tuple[str, str]:
        # rowers are always sorted like ['Entrenador', 'IÑAKI', 'ERRASTI', 'Delegado', 'HASIER', 'Suplentes', ...]
        coach = whitespaces_clean(" ".join(rowers[rowers.index("Entrenador") + 1 : rowers.index("Delegado")]))
        delegate = whitespaces_clean(" ".join(rowers[rowers.index("Delegado") + 1 : rowers.index("Suplentes")]))
        return coach, delegate

    def _get_coxswain_and_bow(self, page: Page, rowers: list[str]) -> tuple[str | None, str | None]:
        """
        Find the coxswain and bow rowers based on their vertical positions on the page.

        Given a Page object and a list of rower names, this method identifies the coxswain (highest vertical position)
        and the bow rower (lowest vertical position) from the provided rower names using their respective positions.

        Parameters:
            page (Page): The Page object representing the page containing the rower instances.
            rowers (List[str]): The list of rower names to search for on the page.

        Returns:
            Tuple[str, str]: A tuple containing the name of the coxswain and the name of the bow rower.

        Raises:
            NotImplementedError: If a rower name appears multiple times on the page.

        Note:
            This method searches for instances of rower names on the provided page and identifies the coxswain as the
            rower with the highest vertical position (lowest on the page) and the bow rower as the rower with the
            lowest vertical position (highest on the page).
        """
        bow = coxswain = None
        lower = 0
        upper = sys.maxsize
        for rower in rowers:
            instances = page.search_for(rower)
            if len(instances) != 1:
                raise NotImplementedError(f"{rower=} appears multiple times in the page")
            _, top, _, _ = instances[0]
            if top < upper:
                upper = top
                bow = rower
            if top > lower:
                lower = top
                coxswain = rower
        return coxswain, bow

    def _get_starboard_and_lardboard(self, page: Page, rowers: list[str]) -> tuple[list[str], list[str]]:
        # sorts the list of rowers from left to right, the first half is lardboard, the other half are starboard
        rowers.sort(key=lambda x: page.search_for(x)[0][0])
        mid = len(rowers) // 2
        return rowers[mid:], rowers[:mid]
