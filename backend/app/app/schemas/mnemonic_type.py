from enum import Enum
from random import choice


class MnemonicType(str, Enum):
    interactive = "interactive"
    fixed = "fixed"
    none = "none"

    @classmethod
    def select_type(cls):
        return choice([MnemonicType.interactive, MnemonicType.fixed, MnemonicType.none])
