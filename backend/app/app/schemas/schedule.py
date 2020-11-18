from typing import Optional

from pydantic import BaseModel


# Properties to receive when updating fact schedule
class Schedule(BaseModel):
    fact_id: int
    debug_id: str
    typed: str
    response: bool
    elapsed_seconds_text: Optional[int] = None
    elapsed_seconds_answer: Optional[int] = None
    elapsed_milliseconds_text: Optional[int] = None
    elapsed_milliseconds_answer: Optional[int] = None
