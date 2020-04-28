from typing import List, Union, Dict, Any, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app import crud, models, schemas
from datetime import datetime
from pytz import timezone

from app.schemas import SuspendType


class CRUDFact(CRUDBase[models.Fact, schemas.FactCreate, schemas.FactUpdate]):
    def get(self, db: Session, id: Any) -> Optional[models.Fact]:
        db_obj = db.query(self.model).filter(models.Fact.fact_id == id).first()
        return db_obj

    def create_with_owner(
        self, db: Session, *, obj_in: schemas.FactCreate, user: models.User
    ) -> models.Fact:
        obj_in_data = jsonable_encoder(obj_in)
        now = datetime.now(timezone('UTC')).isoformat()
        db_obj = self.model(**obj_in_data,
                            user_id=user.id,
                            create_date=now,
                            update_date=now)
        db.add(db_obj)
        db.commit()
        print(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, user: models.User, skip: int = None, limit: int = None
    ) -> List[models.Fact]:
        query = db.query(self.model).filter(models.Fact.user_id == user.id)
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.offset(limit)
        return query.all()

    def update(
        self, db: Session, *, db_obj: models.Fact, obj_in: Union[schemas.FactCreate, Dict[str, Any]]
    ) -> models.Fact:
        update_data = obj_in.dict(exclude_unset=True)
        update_data["update_date"] = datetime.now(timezone('UTC')).isoformat()
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def remove(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        suspend = models.Suspended(suspender=user,
                                   suspended_fact=db_obj,
                                   date_suspended=datetime.now(timezone('UTC')),
                                   suspend_type=SuspendType.delete)
        db.add(suspend)
        db.commit()
        return db_obj

    def suspend(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        suspend = models.Suspended(suspender=user,
                                   suspended_fact=db_obj,
                                   date_suspended=datetime.now(timezone('UTC')),
                                   suspend_type=SuspendType.suspend)
        db.add(suspend)
        db.commit()
        return db_obj

    def report(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        suspend = models.Suspended(suspender=user,
                                   suspended_fact=db_obj,
                                   date_suspended=datetime.now(timezone('UTC')),
                                   suspend_type=SuspendType.report)
        db.add(suspend)
        db.commit()
        return db_obj

    def undo_remove(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended)\
            .filter(and_(models.Suspended.suspended_fact.is_(db_obj),
                         models.Suspended.suspend_type.is_(SuspendType.delete),
                         models.Suspended.suspender.is_(user))).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def undo_suspend(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact.is_(db_obj),
                         models.Suspended.suspend_type.is_(SuspendType.suspend),
                         models.Suspended.suspender.is_(user))).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def undo_report(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact.is_(db_obj),
                         models.Suspended.suspend_type.is_(SuspendType.report),
                         models.Suspended.suspender.is_(user))).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def resolve_report(
            self, db: Session, *, db_obj: models.Fact
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact.is_(db_obj),
                         models.Suspended.suspend_type.is_(SuspendType.report))).delete(synchronize_session=False)
        db.commit()
        return db_obj


fact = CRUDFact(models.Fact)
