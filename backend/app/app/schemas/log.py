from enum import Enum


class Log(str, Enum):
    browser = "browser"
    get_facts = "get_facts"
    update_fact = "update_fact"
    update_user = "update_user"
    study = "study"
    suspend = "suspend"
    delete = "delete"
    report = "report"
    mark = "mark"
    undo_suspend = "undo_suspend"
    undo_delete = "undo_delete"
    undo_report = "undo_report"
    undo_study = "undo_study"  # currently unimplemented
    undo_mark = "undo_mark"
    resolve_report = "resolve_report"
    clear_report_or_suspend = "clear_report_or_suspend"
    assign_viewer = "assign_viewer"
    reassign_model = "reassign_model"
    test_study = "test_study"
    get_test_facts = "get_test_facts"
    get_post_test_facts = "get_post_test_facts"
    post_test_study = "post_test_study"
