from dataclasses import dataclass
from datetime import date
from typing import List, Optional


class Datasource:
    ACT = 'act'
    LGT = 'lgt'
    ARC = 'arc'
    INFOREMO = 'inforemo'

    @classmethod
    def values(cls) -> List[str]:
        return [k for k in cls.__dict__.keys() if not k.startswith('_')]


@dataclass
class LineUpItem:
    race: str
    club: str
    coach: str
    delegate: str
    coxswain: str
    starboard: List[str]
    larboard: List[str]
    substitute: List[str]
    bow: str
