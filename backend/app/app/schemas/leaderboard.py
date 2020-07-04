from typing import List, Union

from pydantic import BaseModel

# Properties to return to client about statistics
from app.schemas import User


class LeaderboardUser(BaseModel):
    user: User
    value: Union[int, float]
    rank: int


class DataTypeHeader(BaseModel):
    text: str
    value: str


class Leaderboard(BaseModel):
    leaderboard: List[LeaderboardUser]
    name: str
    rank_type: str
    headers: List[DataTypeHeader]
    details: str
