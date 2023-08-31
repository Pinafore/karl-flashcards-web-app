from datetime import datetime
from typing import Optional

# Shared properties
from app.schemas import Fact, User
from app.schemas.log import Log
from pydantic import BaseModel


class BothHistoryBase(BaseModel):
    time: datetime
    user_id: int
    fact_id: Optional[int] = None
    details: dict


class HistoryBase(BothHistoryBase):
    log_type: Log
    correct: Optional[bool] = None


class TestHistoryBase(BothHistoryBase):
    response: bool


# Properties to receive on deck creation
class HistoryCreate(HistoryBase):
    pass


class TestHistoryCreate(TestHistoryBase):
    pass


# Properties to receive on deck update
class HistoryUpdate(HistoryBase):
    pass


# Properties to receive on deck update
class TestHistoryUpdate(TestHistoryBase):
    pass


class HistoryInDBBase(HistoryBase):
    id: int


class History(HistoryInDBBase):
    fact: Fact
    user: User

    class Config:
        orm_mode = True
