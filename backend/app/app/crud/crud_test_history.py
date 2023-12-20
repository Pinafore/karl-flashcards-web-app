from app import models, schemas
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session
from app.utils.utils import logger, log_time, time_it


class CRUDTestHistory(CRUDBase[models.Test_History, schemas.TestHistoryCreate, schemas.TestHistoryUpdate]):
    def get_with_debug(self, db: Session, debug_id: str):
        debug = db.query(self.model).filter(self.model.details["debug_id"].astext == debug_id)
        return debug

    def get_user_test_study_count(self, user: models.User):
        return len([history_item for history_item in user.test_history])


test_history = CRUDTestHistory(models.Test_History)
