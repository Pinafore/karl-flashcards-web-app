from typing import Optional, List

from pydantic import BaseModel


class SetParametersSchema(BaseModel):
    repetition_model: str = None
    card_embedding: float = None
    recall: float = None
    recall_target: float = None
    category: float = None
    answer: float = None
    leitner: float = None
    sm2: float = None
    decay_qrep: float = None
    cool_down: float = None
    cool_down_time_correct: float = None
    cool_down_time_wrong: float = None
    max_recent_facts: int = None