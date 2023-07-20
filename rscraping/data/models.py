import json

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Datasource(Enum):
    ACT = "act"
    LGT = "lgt"
    ARC = "arc"

    @classmethod
    def values(cls) -> List[str]:
        return [k for k in cls.__dict__.keys() if not k.startswith("_")]

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.__str__()


class OCR(Enum):
    INFOREMO = "inforemo"

    @classmethod
    def values(cls) -> List[str]:
        return [k for k in cls.__dict__.keys() if not k.startswith("_")]


@dataclass
class Lineup:
    race: str
    club: str
    coach: str
    delegate: str
    coxswain: Optional[str]
    starboard: List[str]
    larboard: List[str]
    substitute: List[str]
    bow: Optional[str]

    def to_json(self) -> str:
        d = {k: v for k, v in self.__dict__.items()}
        return json.dumps(d, indent=4, skipkeys=True, ensure_ascii=False)


@dataclass
class Race:
    name: str
    date: str
    edition: int
    day: int
    modality: str
    type: str
    league: Optional[str]
    town: Optional[str]
    organizer: Optional[str]

    # normalized fields
    trophy_name: str

    # datasource data
    race_id: str
    url: Optional[str]
    datasource: str

    participants: List["Participant"]

    # not available in all the datasource
    race_laps: Optional[int] = None
    race_lanes: Optional[int] = None
    cancelled: bool = False

    def to_json(self) -> str:
        d = {k: v for k, v in self.__dict__.items()}
        d["participants"] = [{k: v for k, v in p.__dict__.items() if k not in ["race"]} for p in d["participants"]]
        return json.dumps(d, indent=4, skipkeys=True, ensure_ascii=False)


@dataclass
class Participant:
    gender: str
    category: str
    club_name: str
    lane: int
    series: int
    laps: List[str]
    distance: Optional[int]

    # normalized fields
    participant: str

    race: Race

    disqualified: bool = False

    def to_json(self) -> str:
        d = {k: v for k, v in self.__dict__.items() if k not in ["race"]}
        return json.dumps(d, indent=4, skipkeys=True, ensure_ascii=False)