import json
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto


@dataclass
class RaceName:
    race_id: str
    name: str


class Datasource(StrEnum):
    ACT = auto()
    LGT = auto()
    ARC = auto()
    TRAINERAS = auto()
    TABULAR = auto()

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value is not None and value.lower() in [d for d in cls]

    @classmethod
    def _missing_(cls, value) -> "Datasource | None":
        if not isinstance(value, str):
            return None
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        return None

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.__str__()


PenaltyDict = dict[str, tuple[str | None, "Penalty | None"]]


@dataclass
class Penalty:
    disqualification: bool
    reason: str | None
    penalty: int = 0

    @classmethod
    def push(
        cls,
        penalties: PenaltyDict,
        club_name: str | None = None,
        time: str | None = None,
        penalty: "Penalty | None" = None,
    ) -> PenaltyDict:
        if not club_name and len(penalties.keys()) == 1:
            club_name = list(penalties.keys())[0]
        if not club_name:
            return penalties

        if club_name in penalties:
            penalties[club_name] = (time or penalties[club_name][0], penalty or penalties[club_name][1])
        else:
            penalties[club_name] = (time, penalty)
        return penalties

    def __str__(self) -> str:
        return self.to_json()

    @staticmethod
    def from_json(json_str: str) -> "Penalty":
        values = json.loads(json_str)
        return Penalty(**values)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class Race:
    name: str
    date: str
    day: int
    modality: str
    type: str
    league: str | None
    town: str | None
    organizer: str | None
    sponsor: str | None

    # normalized fields
    normalized_names: list[tuple[str, int | None]]

    # datasource data
    race_ids: list[str]
    url: str | None
    datasource: str
    gender: str | None

    participants: list["Participant"]

    # not available in all the datasource
    race_notes: str | None = None
    race_laps: int | None = None
    race_lanes: int | None = None
    cancelled: bool = False

    @property
    def year(self) -> int:
        return datetime.strptime(self.date, "%d/%m/%Y").date().year

    def __str__(self) -> str:
        return self.to_json()

    @staticmethod
    def from_json(json_str: str) -> "Race":
        values = json.loads(json_str)
        participants = values["participants"]
        values["participants"] = []

        race = Race(**values)
        if participants:
            race.participants = [Participant(**p, race=race) for p in participants]
        return race

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items()}
        d["participants"] = [p.to_dict() for p in d["participants"]]
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class Participant:
    gender: str
    category: str
    club_name: str
    lane: int | None
    series: int | None
    laps: list[str]
    distance: int | None
    handicap: str | None

    # normalized fields
    participant: str

    race: Race

    penalty: Penalty | None = None

    def __str__(self) -> str:
        return self.to_json()

    @staticmethod
    def from_json(json_str: str) -> "Participant":
        values = json.loads(json_str)
        if "race" not in values:
            values["race"] = None
        return Participant(**values)

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k not in ["race"]}
        d["penalty"] = self.penalty.to_dict() if self.penalty else None
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class Club:
    name: str
    normalized_name: str
    datasource: str
    founding_year: str | None
