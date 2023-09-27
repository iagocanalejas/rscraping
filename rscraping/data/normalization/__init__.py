from .clubs import normalize_club_name  # pyright: ignore
from .races import (
    normalize_race_name,  # pyright: ignore
    normalize_name_parts,  # pyright: ignore
    amend_race_name,  # pyright: ignore
    deacronym_race_name,  # pyright: ignore
    remove_league_indicator,  # pyright: ignore
    remove_race_sponsor,  # pyright: ignore
    remove_day_indicator,  # pyright: ignore
    find_edition,  # pyright: ignore
    find_race_sponsor,  # pyright: ignore
)
from .times import normalize_lap_time, normalize_spanish_months  # pyright: ignore
from .towns import normalize_town, amend_town, remove_province  # pyright: ignore
from .leagues import normalize_league_name  # pyright: ignore
