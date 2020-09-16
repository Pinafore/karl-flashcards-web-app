from typing import List, Union, Optional

from pydantic import BaseModel

# Properties to return to client about statistics
from app.schemas import User, RankType


class IntOrFloat(float):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, float) or isinstance(v, int):
            return v
        raise TypeError('int or float required')


class LeaderboardUser(BaseModel):
    user: User
    value: IntOrFloat
    rank: int


class DataTypeHeader(BaseModel):
    text: str
    value: str
    width: Optional[str] = None


class Leaderboard(BaseModel):
    leaderboard: List[LeaderboardUser]
    total: int
    name: str
    headers: List[DataTypeHeader]
    details: str
    rank_type: RankType
    user: Optional[User] = None
    user_place: Optional[int] = None
    skip: Optional[int] = 0
    limit: Optional[int] = None
