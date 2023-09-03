from enum import Enum


class RankType(str, Enum):
    new_facts = "new_facts"
    reviewed_facts = "reviewed_facts"
    total_seen = "total_seen"
    total_minutes = "total_minutes"
    elapsed_minutes_text = "elapsed_minutes_text"
    new_known_rate = "new_known_rate"
    review_known_rate = "review_known_rate"
    known_rate = "known_rate"
    n_days_studied = "n_days_studied"
