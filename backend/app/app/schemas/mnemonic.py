from datetime import datetime
from typing import List, Optional, Set
from enum import Enum
from pydantic import BaseModel, validator
from sqlalchemy.orm import Query

from app.schemas.repetition import Repetition
from app.schemas.deck import Deck
# Shared properties
from app.schemas.permission import Permission
from app.schemas.target_window import TargetWindow


class MnemonicLearningFeedbackLog(BaseModel):
    study_id: int
    fact_id: int
    user_id: int
    user_rating: Optional[int] = None
    is_offensive: Optional[bool] = None
    is_incorrect_definition: Optional[bool] = None
    is_difficult_to_understand: Optional[bool] = None
    is_bad_keyword_link: Optional[bool] = None
    is_bad_for_other_reason: Optional[bool] = None
    other_reason_text: Optional[str] = None
    correct: bool

class MnemonicComparisonLog(str, Enum):
    a_better = 'a_better'
    b_better = 'b_better'
    equal = 'equal'

class MnemonicComparisonFeedbackLog(BaseModel):
    study_id: int
    fact_id: int
    user_id: int
    mnemonic_a: str
    mnemonic_b: str
    mnemonic_choice: MnemonicComparisonLog

class MnemonicFeedback(BaseModel):
    fact_ids: List[int]
    user_id: int
