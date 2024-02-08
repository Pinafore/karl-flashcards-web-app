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
    user_rating: int
    is_offensive: bool
    is_incorrect_definition: bool
    is_difficult_to_understand: bool
    is_bad_phonetic_keyword: bool
    is_bad_circular_keyword: bool
    is_bad_keyword_explanation: bool
    is_bad_for_other_reason: bool
    other_reason_text: str
    correct: bool
    mnemonic_used_id: str
    mnemonic_used_text: str

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
    comparison_rating: Optional[MnemonicComparisonLog] = None
    passed_sanity_check: Optional[bool] = None
    correct: bool

class MnemonicFeedback(BaseModel):
    fact_ids: List[int]
    user_id: int

class MnemonicFeedbackDetailed(BaseModel):
    fact_ids_learning: List[int]
    fact_ids_comparison: List[int]
    user_id: int

class MnemonicStatistics(BaseModel):
    user_id: int
    num_vocab_studied: int
    num_mnemonics_rated: int