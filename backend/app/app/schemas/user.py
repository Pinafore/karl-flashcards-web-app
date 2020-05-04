from typing import Optional, List, Collection, Any, Type

from pydantic import BaseModel, EmailStr
from pydantic.utils import GetterDict

from .repetition import Repetition
from .deck import DeckInDB, Deck
from .fact import FactInDB, Fact


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: bool = True
    repetition_model: Optional[Repetition] = None


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
    password: Optional[str] = None
    default_deck_id: Optional[int] = None


class SuperUserUpdate(UserUpdate):
    is_superuser: Optional[bool] = None


class UserInDBBase(UserBase):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    default_deck: Deck
    decks: List[Deck] = []
    suspended_facts: List[Fact] = []


    class Config:
        orm_mode = True

    # Done to work with association proxies, which return Collections
    # See here: https://github.com/samuelcolvin/pydantic/issues/380#issuecomment-535112498
    class CustomGetterDict(GetterDict):
        def get(self, item: Any, default: Any) -> Any:
            attribute = getattr(self._obj, item, default)
            if item == "decks":
                attribute = list(attribute)
            if item == "suspended_facts":
                attribute = list(attribute)
            return attribute

    @classmethod
    def _decompose_class(cls: Type['Model'], obj: Any) -> GetterDict:
        return User.CustomGetterDict(obj)


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
