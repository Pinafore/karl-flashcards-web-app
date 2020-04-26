from typing import Optional, List

from pydantic import BaseModel, EmailStr

from .repetition import Repetition
from .deck import DeckInDB, Deck
from .fact import FactInDB, Fact


# Shared properties
class UserBase(BaseModel):
    email: EmailStr = None
    username: str = None
    is_active: bool = True
    repetition_model: Repetition = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str
    repetition_model: Repetition = Repetition.select_model()


# Properties to receive on fact creation
class SuperUserCreate(UserCreate):
    is_superuser: bool = False


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str = None


class SuperUserUpdate(UserBase):
    is_superuser: bool = None


class UserInDBBase(UserBase):
    id: int
    is_superuser: bool

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    default_deck: Deck
    decks: List[Deck]
    suspended: List[Fact] = None


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
