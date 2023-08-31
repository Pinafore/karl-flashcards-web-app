from datetime import datetime
from typing import Optional, List, Any, Type

from pydantic import BaseModel, EmailStr
from pydantic.utils import GetterDict

from .deck import Deck
from .fact import Fact
from .repetition import Repetition


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: bool = True
    repetition_model: Optional[Repetition] = None
    show_help: Optional[bool] = None
    dark_mode: Optional[bool] = None
    pwa_tip: Optional[bool] = None
    beta_user: Optional[bool] = None
    recall_target: Optional[int] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str
    repetition_model: Optional[Repetition] = None


# Properties to receive on creation from super users
class SuperUserCreate(UserCreate):
    is_superuser: bool = False
    beta_user: bool = False


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
    show_help: bool
    dark_mode: bool
    pwa_tip: bool
    beta_user: bool
    recall_target: int

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    default_deck: Deck
    decks: List[Deck] = []

    class Config:
        orm_mode = True

    # Done to work with association proxies, which return Collections
    # See here: https://github.com/samuelcolvin/pydantic/issues/380#issuecomment-535112498
    class CustomGetterDict(GetterDict):
        def get(self, item: Any, default: Any) -> Any:
            attribute = getattr(self._obj, item, default)
            if item == "decks":
                attribute = list(attribute)
            return attribute

    @classmethod
    def _decompose_class(cls: Type['Model'], obj: Any) -> GetterDict:
        return User.CustomGetterDict(obj)


# Additional properties to return via API
class UserWithStudySet(User):
    # Could refactor to return a study set object, but obstacle is circular references
    study_set_expiry_date: Optional[datetime]
    # in_test_mode: bool


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
