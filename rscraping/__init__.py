from typing import List, Optional
from rscraping.clients import Client
from rscraping.data.models import Datasource, Lineup, Race


def find_lineup(race_id: str, datasource: Datasource, is_female: bool) -> List[Lineup]:
    client = Client(source=datasource, is_female=is_female)  # type: ignore
    return client.get_lineup_by_race_id(race_id)


def find_race(race_id: str, datasource: Datasource, is_female: bool, day: Optional[int] = None) -> Optional[Race]:
    client = Client(source=datasource, is_female=is_female)  # type: ignore
    return client.get_race_by_id(race_id, is_female=is_female, day=day)
