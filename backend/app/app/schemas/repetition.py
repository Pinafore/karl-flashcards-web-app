from enum import Enum
from random import choice


class Repetition(str, Enum):
    leitner = "leitner"
    sm2 = "sm-2"
    karl = "karl"
    karl50 = "karl50"
    karl85 = "karl85"

    @classmethod
    def select_model(cls):
        return choice(list(cls.__members__.values()))
