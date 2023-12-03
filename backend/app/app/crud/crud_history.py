from app import models, schemas
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session
from app.utils.utils import logger, log_time, time_it
from sqlalchemy import func, desc, case, cast, String


class CRUDHistory(CRUDBase[models.History, schemas.HistoryCreate, schemas.HistoryUpdate]):
    def get_with_debug(self, db: Session, debug_id: str):
        debug = db.query(self.model).filter(self.model.details["debug_id"].astext == debug_id)
        return debug

    # TODO: Add relearning count/better distinction between initial and subsequent relearning
    def get_user_study_count(self, user: models.User):
        return len([history_item for history_item in user.history if history_item.log_type == "study"])

    def get_user_test_study_count(self, user: models.User):
        return len([history_item for history_item in user.history if history_item.log_type == "test_study"])
    
    def get_test_mode_counts(self, db: Session):
        subquery = (
            db.query(
                models.History.user_id,
                func.sum(
                    case(
                        [(models.History.details['set_type'].astext == 'test', 1.0 / 10),
                        (models.History.details['set_type'].astext == 'post_test', 1.0 / 20)],
                        else_=0
                    )
                ).label('num_test_modes_completed')
            )
            .filter(models.History.details['response'].astext == 'true')
            .filter(models.History.details['set_type'].astext.in_(['test', 'post_test']))
            .group_by(models.History.user_id)
            .subquery()
        )

        data = (
            db.query(
                models.User,
                subquery.c.num_test_modes_completed
            )
            .join(models.User, models.User.id == subquery.c.user_id)
            .filter(subquery.c.num_test_modes_completed >= 3)
            .order_by(desc(subquery.c.num_test_modes_completed))
        )

        return data.all()


history = CRUDHistory(models.History)
