from typing import Optional

from pydantic import BaseModel


class DeckBase(BaseModel):
    title: Optional[str] = None


# Properties to receive on deck creation
class DeckCreate(DeckBase):
    title: str


# Properties to receive on creation from super users
class SuperDeckCreate(DeckCreate):
    public: bool = False


# Properties to receive on deck update
class DeckUpdate(DeckBase):
    pass


# Properties to receive on deck update
class SuperDeckUpdate(DeckUpdate):
    public: Optional[bool] = None


# Properties shared by models stored in DB
class DeckInDBBase(DeckBase):
    id: int
    title: str
    public: bool


# Properties to return to client
class Deck(DeckInDBBase):
    class Config:
        orm_mode = True


# Properties properties stored in DB
class DeckInDB(DeckInDBBase):
    pass
