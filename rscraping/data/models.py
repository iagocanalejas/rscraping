import collections
import json
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Dict, List, Optional, Tuple

RaceName = collections.namedtuple("RaceName", ["race_id", "name"])


class Datasource(StrEnum):
    ACT = auto()
    LGT = auto()
    ARC = auto()
    ABE = auto()
    TRAINERAS = auto()
    INFOREMO = auto()

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value is not None and value.lower() in [d for d in cls]

    @classmethod
    def is_OCR(cls, value: str) -> bool:
        return value is not None and value.lower() in [cls.INFOREMO]

    @classmethod
    def _missing_(cls, value: str) -> Optional["Datasource"]:
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        return None

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.__str__()


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
    images: List[str]

    def to_json(self) -> str:
        d = {k: v for k, v in self.__dict__.items()}
        return json.dumps(d, indent=4, skipkeys=True, ensure_ascii=False)


@dataclass
class Race:
    name: str
    date: str
    day: int
    modality: str
    type: str
    league: Optional[str]
    town: Optional[str]
    organizer: Optional[str]
    sponsor: Optional[str]

    # normalized fields
    normalized_names: List[Tuple[str, Optional[int]]]

    # datasource data
    race_id: str
    url: Optional[str]
    datasource: str
    gender: Optional[str]

    participants: List["Participant"]

    # not available in all the datasource
    race_laps: Optional[int] = None
    race_lanes: Optional[int] = None
    cancelled: bool = False

    def to_dict(self) -> Dict:
        d = {k: v for k, v in self.__dict__.items()}
        d["participants"] = [p.to_dict() for p in d["participants"]]
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, skipkeys=True, ensure_ascii=False)


@dataclass
class Participant:
    gender: str
    category: str
    club_name: str
    lane: Optional[int]
    series: Optional[int]
    laps: List[str]
    distance: Optional[int]
    handicap: Optional[str]

    # normalized fields
    participant: str

    race: Race

    disqualified: bool = False

    # extra arguments
    lineup: Optional["Lineup"] = None

    def to_dict(self) -> Dict:
        d = {k: v for k, v in self.__dict__.items() if k not in ["race"]}
        d["lineup"] = {k: v for k, v in self.lineup.__dict__.items() if k not in ["race"]} if self.lineup else None
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, skipkeys=True, ensure_ascii=False)
