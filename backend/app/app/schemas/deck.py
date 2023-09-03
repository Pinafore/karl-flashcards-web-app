from typing import Optional

from fastapi import Query
from pydantic import BaseModel, validator

from app.schemas import DeckType


class DeckBase(BaseModel):
    title: Optional[str] = None


# Properties to receive on deck creation
class DeckCreate(DeckBase):
    title: str


# Properties to receive on creation from super users
class SuperDeckCreate(DeckCreate):
    deck_type: DeckType = DeckType.default
    # hidden: bool = False


# Properties to receive on deck update
class DeckUpdate(DeckBase):
    pass


# Properties to receive on deck update
class SuperDeckUpdate(DeckUpdate):
    deck_type: Optional[DeckType] = None
    # hidden: Optional[bool] = None


# Properties shared by models stored in DB
class DeckInDBBase(DeckBase):
    id: int
    title: str
    deck_type: DeckType
    # hidden: bool


# Properties to return to client
class Deck(DeckInDBBase):
    class Config:
        orm_mode = True


# Properties properties stored in DB
class DeckInDB(DeckInDBBase):
    pass
