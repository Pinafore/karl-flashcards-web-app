from typing import Optional, List

from pydantic import BaseModel

# Properties to receive when updating fact schedule
from app.schemas import History


class Schedule(BaseModel):
    fact_id: int
    typed: str
    response: bool
    recommendation: bool;
    elapsed_seconds_text: Optional[int] = None
    elapsed_seconds_answer: Optional[int] = None
    elapsed_milliseconds_text: Optional[int] = None
    elapsed_milliseconds_answer: Optional[int] = None


class ScheduleResponse(BaseModel):
    # successes: List[History]
    session_complete: bool
