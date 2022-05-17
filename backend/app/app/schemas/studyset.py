from typing import List, Union, Optional, Any

from pydantic import BaseModel, validator

# Properties to return to client about statistics
from sqlalchemy.orm import Query

from app.schemas import User, Fact, Deck
from app import models


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
    all_decks: Any
    all_facts: Any
    unstudied_facts: List[Fact]
    completed: bool
    num_facts: int

    class Config:
        orm_mode = True


class StudySetInDB(StudySetInDBBase):
    pass
