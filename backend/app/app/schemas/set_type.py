from enum import Enum


class SetType(str, Enum):
    test = "test"
    post_test = "post_test"
    normal = "normal"
    single_study = "single_study"