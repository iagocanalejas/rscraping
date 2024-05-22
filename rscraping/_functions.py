from rscraping.clients import Client
from rscraping.data.models import Datasource, Race


def find_race(
    race_id: str,
    datasource: Datasource,
    is_female: bool,
    category: str | None = None,
    table: int | None = None,
) -> Race | None:
    """
    Find a race based on the provided parameters.

    Parameters:
    - race_id (str): The ID of the race to find.
    - datasource (Datasource): The data source to use for retrieving race information.
    - is_female (bool): Whether the race is for females (True) or not (False).
    - category (Optional[str]): The category of the race (optional).
    - table (Optional[int]): The day of the race (optional).

    Returns:
    - Optional[Race]: The found Race object if the race is found, otherwise None.
    """

    client = Client(source=datasource, is_female=is_female, category=category)
    return client.get_race_by_id(race_id, table=table)
