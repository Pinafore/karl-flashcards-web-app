from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Json


# Shared properties
from app.schemas import Fact, User
from app.schemas.deck import Deck
from app.schemas.log import Log


class HistoryBase(BaseModel):
    time: datetime
    user_id: int
    fact_id: int
    log_type: Log
    details: dict


# Properties to receive on deck creation
class HistoryCreate(HistoryBase):
    pass


# Properties to receive on deck update
class HistoryUpdate(HistoryBase):
    pass


class HistoryInDBBase(HistoryBase):
    id: int


class History(HistoryInDBBase):
    fact: Fact
    user: User

    class Config:
        orm_mode = True
