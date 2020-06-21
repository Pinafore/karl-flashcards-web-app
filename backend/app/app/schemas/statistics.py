from pydantic import BaseModel

# Properties to return to client about statistics


class StatisticsBase(BaseModel):
    new_facts: int
    reviewed_facts: int
    total_seen: int
    total_seconds: int
    new_known_rate: float
    review_known_rate: float


# Used to return statistics to users
class Statistics(StatisticsBase):
    username: str
