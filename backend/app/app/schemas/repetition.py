from enum import Enum
from random import choice


class Repetition(str, Enum):
    leitner = "leitner"
    karl = "karl"
    sm2 = "sm-2"
    karl100 = "karl100"
    karl50 = "karl50"
    karl85 = "karl85"
    settles = "settles"

    @classmethod
    def select_model(cls):
        return choice([Repetition.leitner, Repetition.karl, Repetition.settles])
