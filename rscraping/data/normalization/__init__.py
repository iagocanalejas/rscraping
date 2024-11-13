from .clubs import (
    normalize_club_name as normalize_club_name,
    deacronym_club_name as deacronym_club_name,
    remove_club_title as remove_club_title,
    remove_club_sponsor as remove_club_sponsor,
    ensure_b_teams_have_the_main_team_racing as ensure_b_teams_have_the_main_team_racing,
)
from .races import (
    normalize_race_name as normalize_race_name,
    normalize_name_parts as normalize_name_parts,
    normalize_known_race_names as normalize_known_race_names,
    normalize_ko_race_names as normalize_ko_race_names,
    amend_race_name as amend_race_name,
    deacronym_race_name as deacronym_race_name,
    remove_league_indicator as remove_league_indicator,
    remove_race_sponsor as remove_race_sponsor,
    remove_day_indicator as remove_day_indicator,
    find_edition as find_edition,
    split_by_edition_parts as split_by_edition_parts,
    find_race_sponsor as find_race_sponsor,
)
from .times import normalize_lap_time as normalize_lap_time, normalize_spanish_months as normalize_spanish_months
from .towns import (
    normalize_town as normalize_town,
    amend_town as amend_town,
    remove_province as remove_province,
    extract_town as extract_town,
)
from .leagues import normalize_league_name as normalize_league_name, find_league as find_league
from .penalty import (
    is_guest as is_guest,
    is_absent as is_absent,
    is_retired as is_retired,
    is_cancelled as is_cancelled,
    normalize_penalty as normalize_penalty,
    retrieve_penalty_times as retrieve_penalty_times,
)
from .lemmatize import lemmatize as lemmatize
