from datetime import datetime
from typing import List, Optional, Set

from pydantic import BaseModel, validator
from sqlalchemy.orm import Query

from app.schemas.repetition import Repetition
from app.schemas.deck import Deck
# Shared properties
from app.schemas.permission import Permission
from app.schemas.target_window import TargetWindow


class Mnemonic(BaseModel):
    study_id: int
    fact_id: int
    user_id: int
    user_rating: Optional[int] = None
    viewed_mnemonic: Optional[bool] = False
    is_offensive: Optional[bool] = None
    is_incorrect_definition: Optional[bool] = None
    is_difficult_to_understand: Optional[bool] = None
    is_bad_keyword_link: Optional[bool] = None
    correct: bool

class MnemonicFeedback(BaseModel):
    fact_ids: List[int]
    user_id: int