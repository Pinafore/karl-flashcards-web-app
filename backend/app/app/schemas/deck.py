from typing import List, Optional

from pydantic import BaseModel


class DeckBase(BaseModel):
    title: Optional[str] = None
    public: Optional[bool] = None


# Properties to receive on deck creation
class DeckCreate(DeckBase):
    title: str
    public: bool = False
# TODO: Add SuperDeckCreate and move public there

# Properties to receive on deck update
class DeckUpdate(DeckBase):
    pass


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
