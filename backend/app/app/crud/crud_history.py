from app import models, schemas
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session
from app.utils.utils import logger, log_time, time_it


class CRUDHistory(CRUDBase[models.History, schemas.HistoryCreate, schemas.HistoryUpdate]):
    def get_with_debug(self, db: Session, debug_id: str):
        debug = db.query(self.model).filter(self.model.details["debug_id"].astext == debug_id)
        return debug

    # TODO: Add relearning count/better distinction between initial and subsequent relearning
    def get_user_study_count(self, user: models.User):
        return len([history_item for history_item in user.history if history_item.log_type == "study"])

    def get_user_test_study_count(self, user: models.User):
        return len([history_item for history_item in user.history if history_item.log_type == "test_study"])


history = CRUDHistory(models.History)
