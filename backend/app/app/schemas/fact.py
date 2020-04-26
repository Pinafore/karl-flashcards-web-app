from datetime import datetime
from typing import List

from pydantic import BaseModel, Json


# Shared properties
from app.schemas.deck import Deck


class FactBase(BaseModel):
    user_id: int = None
    text: str = None
    answer: str = None
    category: str = None
    extra: Json = None


class KarlFact(FactBase):
    card_id: str
    text: str
    answer: str
    label: str
    history_id: str


class InternalFactBase(FactBase):
    deck_id: int = None
    text: str = None
    answer: str = None
    category: str = None
    identifier: str = None
    answer_lines: List[str] = None


# Properties to receive on fact creation
class FactCreate(InternalFactBase):
    text: str
    answer: str
    deck_id: int


# Properties to receive on fact creation
class SuperUserFactCreate(FactCreate):
    public: bool = False


# Properties to receive on fact update
class FactUpdate(InternalFactBase):
    pass


# Properties to receive on fact update
class SuperUserFactUpdate(FactUpdate):
    public: bool = False


# Properties shared by models stored in DB
class FactInDBBase(InternalFactBase):
    card_id: int
    deck_id: int
    user_id: int
    text: str
    answer: str
    create_date: datetime
    update_date: datetime
    answer_lines: List[str]
    public: bool

    class Config:
        orm_mode = True


# Properties to return to client
class Fact(FactInDBBase):
    deck: Deck


# Additional properties stored in DB
class FactInDB(FactInDBBase):
    pass
