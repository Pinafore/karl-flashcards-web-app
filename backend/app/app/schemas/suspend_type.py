from enum import Enum


class SuspendType(str, Enum):
    delete = "delete"
    suspend = "suspend"
    report = "report"
