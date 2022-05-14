from typing import List, Union, Optional

from pydantic import BaseModel

# Properties to return to client about statistics
from app.schemas import User, Fact, Deck


class StudySetBase(BaseModel):
    is_test: bool = False
    user_id: int
    deck_id: int


class StudySetCreate(StudySetBase):
    pass


class StudySetUpdate(StudySetBase):
    pass


class StudySetInDBBase(StudySetBase):
    id: int


class StudySet(StudySetInDBBase):
    user: User
    deck: Deck
    facts: List[Fact]
    unstudied_facts: List[Fact]
    completed: bool
    num_facts: int

    class Config:
        orm_mode = True


class StudySetInDB(StudySetInDBBase):
    pass
