from enum import Enum
from random import choice


class Repetition(str, Enum):
    leitner = "leitner" # deprecated
    karl = "karl"
    sm2 = "sm-2" # deprecated
    karl100 = "karl100" # deprecated
    karl50 = "karl50" # deprecated
    karl85 = "karl85" # deprecated
    settles = "settles" # deprecated
    fsrs = "fsrs"
    karlAblation = "karl-ablation" 

    @classmethod
    def select_model(cls):
        return choice([Repetition.fsrs, Repetition.karl])
