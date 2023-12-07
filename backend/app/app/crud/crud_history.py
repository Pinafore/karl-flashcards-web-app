from app import models, schemas
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session
from app.utils.utils import logger, log_time, time_it
from sqlalchemy import func, desc, cast, DateTime, text, Integer


class CRUDHistory(
    CRUDBase[models.History, schemas.HistoryCreate, schemas.HistoryUpdate]
):
    def get_with_debug(self, db: Session, debug_id: str):
        debug = db.query(self.model).filter(
            self.model.details["debug_id"].astext == debug_id
        )
        return debug

    # TODO: Add relearning count/better distinction between initial and subsequent relearning
    def get_user_study_count(self, user: models.User):
        return len(
            [
                history_item
                for history_item in user.history
                if history_item.log_type == "study"
            ]
        )

    def get_user_test_study_count(self, user: models.User):
        return len(
            [
                history_item
                for history_item in user.history
                if history_item.log_type == "test_study"
            ]
        )

    def get_test_mode_counts(self, db: Session):
        subquery = (
            db.query(
                models.History.user_id,
                (func.count(models.History.id) / 10).label("num_test_modes_completed"),
                func.max(models.StudySet.create_date).label(
                    "last_study_date"
                ),  # Getting the max date from the studyset table
            )
            .join(
                models.StudySet,
                cast(models.History.details["studyset_id"].astext, Integer)
                == models.StudySet.id,
            )
            .filter(models.History.details["response"].astext == "true")
            .filter(
                models.History.details["set_type"].astext.in_(["test", "post_test"])
            )
            .group_by(models.History.user_id)
            .subquery()
        )

        data = (
            db.query(
                models.User,
                subquery.c.num_test_modes_completed,
                subquery.c.last_study_date,
            )
            .join(models.User, models.User.id == subquery.c.user_id)
            .filter(subquery.c.num_test_modes_completed >= 3)
            .order_by(desc(subquery.c.num_test_modes_completed))
        )

        return data.all()


history = CRUDHistory(models.History)
