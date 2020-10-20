from pydantic import BaseModel

# Properties to return to client about statistics
from app.schemas import User


class StatisticsBase(BaseModel):
    new_facts: int
    reviewed_facts: int
    total_seen: int
    total_minutes: int
    elapsed_minutes_text: int
    known_rate: float
    new_known_rate: float
    review_known_rate: float
    n_days_studied: int


# Used to return statistics to users
class Statistics(StatisticsBase):
    user: User
    name: str
