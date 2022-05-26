from typing import List, Union, Optional, Any

from pydantic import BaseModel, validator

# Properties to return to client about statistics
from sqlalchemy.orm import Query

from app.schemas import User, Fact, Deck


class StudySetBase(BaseModel):
    is_test: bool = False
    user_id: int


class StudySetCreate(StudySetBase):
    pass


class StudySetUpdate(StudySetBase):
    pass


class StudySetInDBBase(StudySetBase):
    id: int


class StudySet(StudySetInDBBase):
    user: User
    all_decks: List[Deck]
    all_facts: List[Fact]
    unstudied_facts: List[Fact]
    completed: bool
    num_facts: int
    num_unstudied: int
    is_first_pass: bool
    short_description: str
    expanded_description: str

    class Config:
        orm_mode = True


class StudySetInDB(StudySetInDBBase):
    pass
