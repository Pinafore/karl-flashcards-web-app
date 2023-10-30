from typing import List, Optional

from pydantic import BaseModel, validator

# Properties to return to client about statistics
from sqlalchemy.orm import Query

from app.schemas import User, Fact, Deck, Repetition, SetType


class StudySetBase(BaseModel):
    user_id: int
    debug_id: Optional[str]
    repetition_model: Optional[Repetition]
    set_type: Optional[SetType]


class StudySetCreate(StudySetBase):
    repetition_model: Repetition
    set_type: SetType = SetType.normal


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
    # retired: bool
    set_type: SetType

    class Config:
        orm_mode = True


class StudySetInDB(StudySetInDBBase):
    pass
