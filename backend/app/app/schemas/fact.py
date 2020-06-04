from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Json


# Shared properties
from app.schemas.deck import Deck


class FactBase(BaseModel):
    text: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None


class KarlFact(FactBase):
    user_id: int
    fact_id: int
    text: str
    answer: str
    deck_name: str
    label: Optional[str] = None
    history_id: Optional[int] = None
    env: str


class InternalFactBase(FactBase):
    deck_id: Optional[int] = None
    identifier: Optional[str] = None
    answer_lines: List[str] = None
    extra: Optional[dict] = None


# Properties to receive on fact creation
class FactCreate(InternalFactBase):
    text: str
    answer: str
    deck_id: int
    answer_lines: List[str]


# Properties to receive on fact update
class FactUpdate(InternalFactBase):
    pass


# Properties to receive on fact search
class FactSearch(InternalFactBase):
    deck_ids: Optional[List[int]] = None
    marked: Optional[bool] = None
    all_suspended: Optional[bool] = None
    suspended: Optional[bool] = None
    reported: Optional[bool] = None
    skip: Optional[int] = None
    limit: Optional[int] = None
    randomize: bool = False


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
    marked: Optional[bool] = None


# Additional properties stored in DB
class FactInDB(FactInDBBase):
    pass
