from typing import List, Union, Dict, Any, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, or_, not_, func
from sqlalchemy.orm import Session, aliased

from app.crud.base import CRUDBase
from app import crud, models, schemas
from datetime import datetime
from pytz import timezone
import time
import requests

import logging

from app.core.config import settings

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

    def get_multi_by_conditions(
            self,
            db: Session,
            *,
            user: Optional[models.User] = None,
            skip: Optional[int] = None,
            limit: Optional[int] = None,
            search: Optional[schemas.FactSearch] = None
    ) -> List[models.Fact]:
        query = db.query(self.model)
        if user:
            query = query.filter(models.Fact.user_id == user.id)
        if search:
            if search.text:
                pass
            if search.deck_ids:
                query = query.join(models.Fact.deck).filter(models.Deck.user_decks.any(owner_id=user.id))
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

    def mark(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:

        mark = models.Marked(marker=user, marked_fact=db_obj, date_marked=datetime.now(timezone('UTC')))
        db.add(mark)
        db.commit()
        return db_obj

    def undo_remove(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact == db_obj,
                         models.Suspended.suspend_type == schemas.SuspendType.delete,
                         models.Suspended.suspender == user)).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def undo_suspend(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact == db_obj,
                         models.Suspended.suspend_type == schemas.SuspendType.suspend,
                         models.Suspended.suspender == user)).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def undo_report(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact == db_obj,
                         models.Suspended.suspend_type == schemas.SuspendType.report,
                         models.Suspended.suspender == user)).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def resolve_report(
            self, db: Session, *, db_obj: models.Fact
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact == db_obj,
                         models.Suspended.suspend_type == schemas.SuspendType.report)).delete(
            synchronize_session=False)
        db.commit()
        return db_obj

    def undo_mark(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Marked) \
            .filter(and_(models.Marked.marked_fact == db_obj,
                         models.Marked.marker == user)).delete(synchronize_session=False)
        db.commit()
        return db_obj

    def get_eligible_facts(
            self, db: Session, *, user: models.User, filters: schemas.FactSearch = schemas.FactSearch()
    ) -> List[models.Fact]:
        begin_overall_start = time.time()
        user_facts = (db.query(models.Fact).filter(models.Fact.user_id == user.id))
        visible_decks = (
            db.query(models.Deck.id).join(models.User_Deck).filter(models.User_Deck.owner_id == user.id).subquery())
        deck_owners = (db.query(models.User_Deck.deck_id, models.User_Deck.owner_id)
                       .outerjoin(visible_decks)
                       .filter(models.User_Deck.permissions == schemas.Permission.owner).subquery())
        filtered_facts = (db.query(models.Fact)
                          .join(visible_decks, models.Fact.deck_id == visible_decks.c.id)
                          .join(deck_owners,
                                and_(models.Fact.deck_id == deck_owners.c.deck_id,
                                     models.Fact.user_id == deck_owners.c.owner_id)))
        facts_query = (user_facts.union(filtered_facts))
        if filters.all_suspended:
            facts_query = facts_query.filter(not_(models.Fact.suspenders.any(id=user.id)))
        else:
            facts_query = facts_query.outerjoin(models.Suspended)
            if filters.suspended:
                facts_query = facts_query.filter(models.Suspended.suspend_type == schemas.SuspendType.suspend)
            elif filters.reported:
                facts_query = facts_query.filter(models.Suspended.suspend_type == schemas.SuspendType.report)
            else:
                facts_query = facts_query.filter(models.Suspended.suspend_type != schemas.SuspendType.delete)
        if filters.text:
            facts_query = facts_query.filter(models.Fact.text.ilike(filters.text))
        if filters.answer:
            facts_query = facts_query.filter(models.Fact.answer.ilike(filters.answer))
        if filters.category:
            facts_query = facts_query.filter(models.Fact.category.ilike(filters.category))
        if filters.identifier:
            facts_query = facts_query.filter(models.Fact.identifier.ilike(filters.identifier))
        if filters.deck_ids:
            facts_query = facts_query.filter(models.Fact.deck_id.in_(filters.deck_ids))
        if filters.deck_id:
            facts_query = facts_query.filter(models.Fact.deck_id == filters.deck_id)
        if filters.marked:
            facts_query = facts_query.filter(models.Fact.markers.any(id=user.id))
        if filters.randomize:
            facts_query = facts_query.order_by(func.random())
        if filters.skip:
            facts_query = facts_query.skip(filters.skip)
        if filters.limit:
            facts_query = facts_query.limit(filters.limit)
        logger.info("Finished writing queries: " + str(time.time() - begin_overall_start))
        facts = facts_query.all()
        overall_end_time = time.time()
        overall_total_time = overall_end_time - begin_overall_start
        logger.info("overall time: " + str(overall_total_time))
        return facts

    def get_study_set(
            self,
            db: Session,
            *,
            user: models.User,
            deck_ids: List[int] = None,
            return_limit: Optional[int] = None,
            send_limit: Optional[int] = 100,
    ) -> List[schemas.Fact]:
        filters = schemas.FactSearch(deck_ids=deck_ids, limit=send_limit, all_suspended=True)
        eligible_facts = self.get_eligible_facts(db, user=user, filters=filters)

        karl_list = []
        karl_list_start = time.time()
        for each_card in eligible_facts:
            karl_list.append(schemas.KarlFact(
                text=each_card.text,
                answer=each_card.answer,
                category=each_card.category,
                deck_name=each_card.deck.title,
                user_id=user.id,
                fact_id=each_card.fact_id,
                env=settings.ENVIRONMENT
            ).dict())
        logger.info("eligible fact time: " + str(time.time() - karl_list_start))

        karl_query_start = time.time()
        scheduler_response = requests.post(settings.INTERFACE + "api/karl/schedule", json=karl_list)
        response_json = scheduler_response.json()
        card_order = response_json["order"]
        rationale = response_json["rationale"]
        logger.info("query time: " + str(time.time() - karl_query_start))

        facts = []
        if rationale != "<p>no fact received</p>":
            if settings.ENVIRONMENT == "dev":
                logger.info(karl_list)
                logger.info(scheduler_response.json())
                logger.info("First order: " + str(card_order[0]))
                logger.info("First card: " + str(karl_list[card_order[0]]))
                logger.info("rationale:" + str(rationale))
            reordered_karl_list = [karl_list[x] for x in card_order]
            if return_limit:
                for _, each_karl_fact in zip(range(return_limit), reordered_karl_list):
                    retrieved_fact = self.get(db=db, id=int(each_karl_fact["fact_id"]))
                    fact_schema = schemas.Fact.from_orm(retrieved_fact)
                    fact_schema.rationale = rationale
                    if retrieved_fact:
                        fact_schema.marked = True if user in retrieved_fact.markers else False
                    facts.append(fact_schema)
            else:
                for each_karl_fact in reordered_karl_list:
                    retrieved_fact = self.get(db=db, id=int(each_karl_fact["fact_id"]))
                    fact_schema = schemas.Fact.from_orm(retrieved_fact)
                    fact_schema.rationale = rationale
                    print(retrieved_fact)
                    # MARK: maybe not the most efficient solution for determining if user has marked a fact
                    if retrieved_fact:
                        fact_schema.marked = True if user in retrieved_fact.markers else False
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
            deck_name=db_obj.deck.title,
            answer=db_obj.answer,
            env=settings.ENVIRONMENT,
            label=response).dict()]
        request = requests.post(settings.INTERFACE + "api/karl/update", json=payload_update)
        if 200 <= request.status_code < 300:
            return True
        else:
            return False


fact = CRUDFact(models.Fact)
