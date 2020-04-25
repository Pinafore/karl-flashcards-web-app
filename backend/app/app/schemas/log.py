from enum import Enum


class Log(str, Enum):
    study = "study"
    suspend = "suspend"
    delete = "delete"
    report = "report"
    unsuspend = "unsuspend"
    undo_delete = "undo_delete"
    resolve_report = "resolve_report"
    undo_study = "undo_study"
