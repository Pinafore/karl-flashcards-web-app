from typing import Optional

from pydantic import BaseModel


# Properties to return to client about statistics
from app import schemas


class StatisticsBase(BaseModel):
    new_known_rate: float = None
    review_known_rate: float = None
    new_facts: int
    reviewed_facts: int
    total_seen: int
    total_seconds: int


# Used in call to internal API
class StatisticsCall(StatisticsBase):
    user_id: int
    new_known_rate: float = None
    review_known_rate: float = None
    new_facts: int
    reviewed_facts: int
    total_seen: int
    total_seconds: int


# Used to return statistics to users
class Statistics(StatisticsBase):
    user: schemas.User
    new_known_rate: float = None
    review_known_rate: float = None
    new_facts: int
    reviewed_facts: int
    total_seen: int
    total_seconds: int