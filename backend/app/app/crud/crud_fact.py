import json
from typing import List, Union, Dict, Any, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app import crud, models, schemas, evaluate
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
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, user: models.User, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[models.Fact]:
        query = db.query(self.model).filter(models.Fact.user_id == user.id)
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.offset(limit)
        return query.all()

    def update(
        self, db: Session, *, db_obj: models.Fact, obj_in: Union[schemas.FactUpdate, Dict[str, Any]]
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
                not_(or_(
                    models.Fact.suspensions.any(suspend_type=schemas.SuspendType.report),
                    models.Fact.suspenders.any(id=user.id)
                ))
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
            self, db: Session, *, user: models.User, deck_ids: List[int] = None, limit: Optional[int] = None
    ) -> List[schemas.Fact]:
        eligible_facts = self.get_eligible_facts(db, user=user, deck_ids=deck_ids, limit=limit)

        karl_list = []
        karl_list_start = time.time()
        for each_card in eligible_facts:
            karl_list.append(schemas.KarlFact(
                text=each_card.text,
                answer=each_card.answer,
                category=each_card.category,
                user_id=user.id,
                fact_id=each_card.fact_id
            ).dict())
        logger.info("eligible fact time: " + str(time.time() - karl_list_start))

        karl_query_start = time.time()
        scheduler_response = requests.post("http://host.docker.internal:4000/api/karl/schedule", json=karl_list)
        logger.info(scheduler_response.json())
        response_json = scheduler_response.json()
        card_order = response_json["order"]
        rationale = response_json["rationale"]
        logger.info("query time: " + str(time.time() - karl_query_start))

        reordered_karl_list = [karl_list[x] for x in card_order]

        facts = []
        for _, each_karl_fact in zip(range(limit), reordered_karl_list):
            retrieved_fact = self.get(db=db, id=int(each_karl_fact["fact_id"]))
            fact_schema = schemas.Fact.from_orm(retrieved_fact)
            fact_schema.rationale = rationale
            facts.append(fact_schema)
        return facts

    def update_schedule(
            self, db: Session, *, user: models.User, db_obj: models.Fact, schedule: schemas.Schedule
    ) -> bool:
        response = schedule.response
        date_studied = datetime.now(timezone('UTC')).isoformat()
        details = {
            "study_system": "karl",
            "typed": schedule.typed,
            "response": schedule.response,
            "elapsed_seconds_text": schedule.elapsed_seconds_text,
            "elapsed_seconds_answer": schedule.elapsed_seconds_answer
        }
        history_in = schemas.HistoryCreate(
            time=date_studied,
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.study,
            details=details

        )
        history = crud.history.create(db=db, obj_in=history_in)
        payload_update = [schemas.KarlFact(
            text=db_obj.text,
            user_id=user.id,
            fact_id=db_obj.fact_id,
            history_id=history.id,
            category=db_obj.category,
            answer=db_obj.answer,
            label=response).dict()]
        request = requests.post("http://host.docker.internal:4000/api/karl/update", json=payload_update)
        if 200 <= request.status_code < 300:
            return True
        else:
            return False


fact = CRUDFact(models.Fact)
