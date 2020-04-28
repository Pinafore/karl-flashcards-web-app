from typing import List, Union, Dict, Any, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app import crud, models, schemas
from datetime import datetime
from pytz import timezone
import time
import requests

import logging

from app.schemas import Permission

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                                   suspend_type=schemas.SuspendType.delete)
        db.add(suspend)
        db.commit()
        return db_obj

    def suspend(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        suspend = models.Suspended(suspender=user,
                                   suspended_fact=db_obj,
                                   date_suspended=datetime.now(timezone('UTC')),
                                   suspend_type=schemas.SuspendType.suspend)
        db.add(suspend)
        db.commit()
        return db_obj

    def report(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        suspend = models.Suspended(suspender=user,
                                   suspended_fact=db_obj,
                                   date_suspended=datetime.now(timezone('UTC')),
                                   suspend_type=schemas.SuspendType.report)
        db.add(suspend)
        db.commit()
        return db_obj

    def undo_remove(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended)\
            .filter(and_(models.Suspended.suspended_fact.is_(db_obj),
                         models.Suspended.suspend_type.is_(schemas.SuspendType.delete),
                         models.Suspended.suspender.is_(user))).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def undo_suspend(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact.is_(db_obj),
                         models.Suspended.suspend_type.is_(schemas.SuspendType.suspend),
                         models.Suspended.suspender.is_(user))).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def undo_report(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact.is_(db_obj),
                         models.Suspended.suspend_type.is_(schemas.SuspendType.report),
                         models.Suspended.suspender.is_(user))).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def resolve_report(
            self, db: Session, *, db_obj: models.Fact
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact.is_(db_obj),
                         models.Suspended.suspend_type.is_(schemas.SuspendType.report))).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def get_eligible_facts(
            self, db: Session, *, user: models.User, deck_ids: List[int] = None, limit: int
    ) -> List[models.Fact]:
        begin_overall_start = time.time()

        # Queries for suspended cards
        logger.info("Get eligible fact start: " + str(datetime.now(timezone('UTC'))))
        # suspended_subquery = db.query(models.Suspended.suspended_fact)
        # owner_subquery = db.query(models.User_Deck.owner_id).join(models.Fact).filter()
        facts_query = db.query(models.Fact).join(models.Fact.deck).filter(
            and_(
                or_(
                    models.Fact.user_id == user.id,
                    models.Deck.user_decks.any(permissions=schemas.Permission.owner),
                ),
                or_(
                    models.Fact.suspensions.any(suspend_type=schemas.SuspendType.report),
                    models.Fact.suspenders.any(id=user.id)
                )
            )
        )

        if deck_ids:
            facts_query = facts_query.filter(models.Deck.id.in_(deck_ids))
        if limit:
            facts_query = facts_query.limit(limit)
        facts = facts_query.all()
        overall_end_time = time.time()
        overall_total_time = overall_end_time - begin_overall_start
        logger.info("overall time: " + str(overall_total_time))
        return facts

    def get_study_set(
            self, db: Session, *, user: models.User, deck_ids: List[int] = None, limit: int = None
    ) -> List[models.Fact]:
        eligible_facts = self.get_eligible_facts(db, user=user, deck_ids=deck_ids, limit=limit)

        karl_list = []
        karl_list_start = time.time()
        for each_card in eligible_facts:
            karl_list.append(schemas.KarlFact(
                text=each_card.text,
                user_id=user.id,
                fact_id=each_card.fact_id,
                category=each_card.category,
                answer=each_card.answer
            ).dict())
        karl_list_end_time = time.time()
        overall_karl_list_time = karl_list_end_time - karl_list_start
        logger.info("eligible fact time: " + str(overall_karl_list_time))

        karl_query_start = time.time()
        scheduler_response = requests.post("http://172.17.0.1:4000/api/karl/schedule", json=karl_list)
        logger.info(scheduler_response.text)
        response_json = scheduler_response.json()
        card_order = response_json["order"]
        rationale = response_json["rationale"]
        karl_query_end_time = time.time()
        overall_karl_query_time = karl_query_end_time - karl_query_start
        logger.info("query time: " + str(overall_karl_query_time))

        reordered_karl_list = [karl_list[x] for x in card_order]

        facts = []
        for _, each_karl_fact in zip(range(limit), reordered_karl_list):
            retrieved_fact = self.get(db=db, id=int(each_karl_fact["card_id"]))
            fact = schemas.Fact.from_orm(retrieved_fact)
            fact.rationale = rationale
            facts.append(fact)
        return facts

    def update_schedule(
            self, db: Session, *, user: models.User, fact: models.Fact, fact_in: schemas.FactScheduleUpdate
    ) -> List[models.Fact]:
        facts = []
        return facts


fact = CRUDFact(models.Fact)
