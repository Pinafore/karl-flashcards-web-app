from datetime import datetime

from pydantic import BaseModel, Json


# Shared properties
from app.schemas.deck import Deck


class FactBase(BaseModel):
    deck_id: int = None
    user_id: int = None
    text: str = None
    answer: str = None
    category: str = None
    identifier: str = None
    answer_lines: [str] = None
    extra: Json = None


# Properties to receive on fact creation
class FactCreate(FactBase):
    text: str
    answer: str
    deck_id = int


# Properties to receive on fact creation
class SuperUserFactCreate(FactCreate):
    public: bool


# Properties to receive on fact update
class FactUpdate(FactBase):
    pass


# Properties shared by models stored in DB
class FactInDBBase(FactBase):
    id: int
    deck_id: int
    user_id: int
    text: str
    answer: str
    create_date: datetime
    update_date: datetime
    answer_lines: [str]
    public: bool

    class Config:
        orm_mode = True


# Properties to return to client
class Fact(FactInDBBase):
    deck: Deck


# Additional properties stored in DB
class FactInDB(FactInDBBase):
    pass
