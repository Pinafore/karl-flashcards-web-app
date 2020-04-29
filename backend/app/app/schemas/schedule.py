from typing import Optional

from pydantic import BaseModel


# Properties to receive when updating fact schedule
class Schedule(BaseModel):
    fact_id: int
    typed: str
    response: bool
    elapsed_seconds_text: int
    elapsed_seconds_answer: int
