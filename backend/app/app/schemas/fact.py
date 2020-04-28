from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Json


# Shared properties
from app.schemas.deck import Deck


class FactBase(BaseModel):
    text: str = None
    answer: str = None
    category: str = None
    extra: dict = None


class KarlFact(FactBase):
    fact_id: str
    text: str
    answer: str
    label: str = None
    history_id: str = None


class InternalFactBase(FactBase):
    deck_id: int = None
    identifier: str = None
    answer_lines: List[str] = None


# Properties to receive on fact creation
class FactCreate(InternalFactBase):
    text: str
    answer: str
    deck_id: int
    answer_lines: List[str]


# Properties to receive on fact update
class FactUpdate(InternalFactBase):
    pass

# Properties to receive when updating fact schedule
class FactScheduleUpdate(InternalFactBase):
    typed: str
    response: str
    review_datetime: datetime
    elapsed_seconds_front: int
    elapsed_seconds_back: int

# Properties shared by models stored in DB
class FactInDBBase(InternalFactBase):
    fact_id: int
    deck_id: int
    user_id: int
    text: str
    answer: str
    create_date: datetime
    update_date: datetime
    answer_lines: List[str]
    deck: Deck

    class Config:
        orm_mode = True


# Properties to return to client
class Fact(FactInDBBase):
    rationale: Optional[str] = None


# Additional properties stored in DB
class FactInDB(FactInDBBase):
    pass
