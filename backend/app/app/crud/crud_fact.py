import json
import logging
import time
from datetime import datetime
from tempfile import SpooledTemporaryFile
from typing import List, Union, Dict, Any, Optional

import pandas
import requests
from fastapi.encoders import jsonable_encoder
from pytz import timezone
from sentry_sdk import capture_exception
from sqlalchemy import and_, not_, func
from sqlalchemy.orm import Session, Query

from app import crud, models, schemas
from app.core.config import settings
from app.crud.base import CRUDBase
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDFact(CRUDBase[models.Fact, schemas.FactCreate, schemas.FactUpdate]):
    def get(self, db: Session, id: Any) -> Optional[models.Fact]:
        db_obj = db.query(self.model).filter(models.Fact.fact_id == id).first()
        return db_obj

    def get_schema_with_perm(self, db_obj: models.Fact, user: models.User):
        schema = schemas.Fact.from_orm(db_obj)
        schema.permission = db_obj.permissions(user)
        schema.marked = db_obj.is_marked(user)
        schema.suspended = db_obj.is_suspended(user)
        schema.reports = db_obj.find_reports(user)
        return schema

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
            self,
            db: Session,
            *,
            user: Optional[models.User] = None,
            skip: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> List[models.Fact]:
        query = db.query(self.model)
        if user:
            query = query.filter(models.Fact.user_id == user.id)
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
        now = datetime.now(timezone('UTC'))
        delete = models.Deleted(deleter=user, deleted_fact=db_obj, date_deleted=now)
        db.add(delete)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=now,
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.delete,
            details={"study_system": "karl"}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def suspend(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        now = datetime.now(timezone('UTC'))
        suspend = models.Suspended(suspender=user,
                                   suspended_fact=db_obj,
                                   date_suspended=now)
        db.add(suspend)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=now,
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.suspend,
            details={"study_system": "karl"}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def report(
            self, db: Session, *, db_obj: models.Fact, user: models.User, suggestion: schemas.FactToReport
    ) -> models.Fact:
        now = datetime.now(timezone('UTC'))
        report = models.Reported(reporter=user,
                                 reported_fact=db_obj,
                                 date_reported=datetime.now(timezone('UTC')),
                                 suggestion=suggestion)
        db.add(report)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=now,
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.report,
            details={"study_system": "karl"}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def mark(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        now = datetime.now(timezone('UTC'))

        mark = models.Marked(marker=user, marked_fact=db_obj, date_marked=now)
        db.add(mark)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=now,
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.mark,
            details={"study_system": "karl"}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def undo_remove(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Deleted).filter(
            and_(models.Deleted.fact_id == db_obj.fact_id, models.Deleted.user_id == user.id)).delete(
            synchronize_session=False)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.undo_delete,
            details={"study_system": "karl"}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def undo_suspend(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact == db_obj,
                         models.Suspended.suspender == user)).delete(synchronize_session=False)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.undo_suspend,
            details={"study_system": "karl"}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def undo_report(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:

        db.query(models.Reported) \
            .filter(and_(models.Reported.fact_id == db_obj.fact_id,
                         models.Reported.user_id == user.id)).delete(synchronize_session=False)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.undo_report,
            details={"study_system": "karl"}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def resolve_report(
            self, db: Session, *, user: models.User, db_obj: models.Fact
    ) -> models.Fact:
        db.query(models.Reported) \
            .filter(models.Reported.fact_id == db_obj.fact_id).delete(
            synchronize_session=False)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.resolve_report,
            details={"study_system": "karl"}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def undo_mark(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Marked) \
            .filter(and_(models.Marked.marked_fact == db_obj,
                         models.Marked.marker == user)).delete(synchronize_session=False)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.undo_mark,
            details={"study_system": "karl"}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def build_facts_query(self, db: Session, *, user: models.User, filters: schemas.FactSearch = schemas.FactSearch()):
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
        if filters.studyable:
            facts_query = (facts_query
                           .outerjoin(models.Deleted,
                                      and_(models.Fact.fact_id == models.Deleted.fact_id,
                                           models.Deleted.user_id == user.id))
                           .filter(models.Deleted.user_id == None)
                           .outerjoin(models.Reported,
                                      and_(models.Fact.fact_id == models.Reported.fact_id,
                                           models.Reported.user_id == user.id)
                                      )
                           .filter(models.Reported.user_id == None)
                           .outerjoin(models.Suspended,
                                      and_(models.Fact.fact_id == models.Suspended.fact_id,
                                           models.Suspended.user_id == user.id)
                                      )
                           .filter(models.Suspended.user_id == None))
        else:
            facts_query = (facts_query
                           .outerjoin(models.Deleted,
                                      and_(models.Fact.fact_id == models.Deleted.fact_id,
                                           models.Deleted.user_id == user.id))
                           .filter(models.Deleted.user_id == None))
            if filters.suspended is not None:
                if filters.suspended:
                    facts_query = facts_query.join(models.Suspended).filter(models.Suspended.user_id == user.id)
                else:
                    facts_query = (facts_query
                                   .outerjoin(models.Suspended,
                                              and_(models.Fact.fact_id == models.Suspended.fact_id,
                                                   models.Suspended.user_id == user.id)
                                              )
                                   .filter(models.Suspended.user_id == None))

            if filters.reported is not None:
                if filters.reported:
                    facts_query = facts_query.join(models.Reported)
                    if not user.is_superuser:
                        facts_query = facts_query.filter(models.Reported.user_id == user.id)
                else:
                    facts_query = (facts_query
                                   .outerjoin(models.Reported,
                                              and_(models.Fact.fact_id == models.Reported.fact_id,
                                                   models.Reported.user_id == user.id)
                                              )
                                   .filter(models.Reported.user_id == None))
        if filters.all:
            facts_query = facts_query.filter(
                models.Fact.__ts_vector__.op('@@')(func.plainto_tsquery('english', filters.all)))
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
        if filters.marked is not None:
            if filters.marked:
                facts_query = facts_query.filter(models.Fact.markers.any(id=user.id))
            else:
                facts_query = facts_query.filter(not_(models.Fact.markers.any(id=user.id)))
        if filters.randomize:
            facts_query = facts_query.order_by(func.random())
        return facts_query

    def count_eligible_facts(
            self, query: Query
    ) -> int:
        begin_overall_start = time.time()
        facts = query.distinct().count()
        overall_end_time = time.time()
        overall_total_time = overall_end_time - begin_overall_start
        logger.info("overall time count: " + str(overall_total_time))
        return facts

    def get_eligible_facts(
            self, query: Query, skip: int = None, limit: int = None
    ) -> List[models.Fact]:
        begin_overall_start = time.time()
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        facts = query.all()
        overall_end_time = time.time()
        overall_total_time = overall_end_time - begin_overall_start
        logger.info("overall time facts: " + str(overall_total_time))
        return facts

    def get_study_set(
            self,
            db: Session,
            *,
            user: models.User,
            deck_ids: List[int] = None,
            return_limit: Optional[int] = None,
            send_limit: Optional[int] = 100,
    ) -> Union[List[schemas.Fact], requests.exceptions.RequestException, json.decoder.JSONDecodeError]:
        filters = schemas.FactSearch(deck_ids=deck_ids, limit=send_limit, randomize=True, studyable=True)
        query = crud.fact.build_facts_query(db=db, user=user, filters=filters)
        eligible_facts = self.get_eligible_facts(query=query, limit=send_limit)
        if not eligible_facts:
            return []
        karl_list = []
        karl_list_start = time.time()
        for each_card in eligible_facts:
            karl_list.append(schemas.KarlFact(
                text=each_card.text,
                answer=each_card.answer,
                category=each_card.category,
                deck_name=each_card.deck.title,
                deck_id=each_card.deck_id,
                user_id=user.id,
                fact_id=each_card.fact_id,
                env=settings.ENVIRONMENT
            ).dict())
        eligible_fact_time = time.time() - karl_list_start
        logger.info("eligible fact time: " + str(eligible_fact_time))

        karl_query_start = time.time()
        try:
            scheduler_response = requests.post(settings.INTERFACE + "api/karl/schedule", json=karl_list)
            response_json = scheduler_response.json()
            card_order = response_json["order"]
            rationale = response_json["rationale"]

            query_time = time.time() - karl_query_start
            logger.info("query time: " + str(query_time))

            facts = []
            if rationale != "<p>no fact received</p>":
                reordered_karl_list = [karl_list[x] for x in card_order]
                if return_limit:
                    for _, each_karl_fact in zip(range(return_limit), reordered_karl_list):
                        retrieved_fact = self.get(db=db, id=int(each_karl_fact["fact_id"]))
                        fact_schema = self.get_schema_with_perm(db_obj=retrieved_fact, user=user)
                        fact_schema.rationale = rationale
                        if retrieved_fact:
                            fact_schema.marked = True if user in retrieved_fact.markers else False
                        facts.append(fact_schema)
                else:
                    for each_karl_fact in reordered_karl_list:
                        retrieved_fact = self.get(db=db, id=int(each_karl_fact["fact_id"]))
                        fact_schema = self.get_schema_with_perm(db_obj=retrieved_fact, user=user)
                        fact_schema.rationale = rationale
                        # MARK: maybe not the most efficient solution for determining if user has marked a fact
                        if retrieved_fact:
                            fact_schema.marked = retrieved_fact.is_marked(user)
                        facts.append(fact_schema)
            details = {
                "study_system": "karl",
                "first_fact": facts[0] if len(facts) != 0 else "empty",
                "eligible_fact_time": query_time,
                "scheduler_query_time": eligible_fact_time,
            }
            history_in = schemas.HistoryCreate(
                time=datetime.now(timezone('UTC')).isoformat(),
                user_id=user.id,
                log_type=schemas.Log.get_facts,
                details=details

            )
            crud.history.create(db=db, obj_in=history_in)
            return facts
        except requests.exceptions.RequestException as e:
            capture_exception(e)
            return e
        except json.decoder.JSONDecodeError as e:
            capture_exception(e)
            return e

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
            deck_id=db_obj.deck_id,
            answer=db_obj.answer,
            env=settings.ENVIRONMENT,
            elapsed_seconds_text=schedule.elapsed_seconds_text,
            elapsed_seconds_answer=schedule.elapsed_seconds_answer,
            label=response).dict()]
        request = requests.post(settings.INTERFACE + "api/karl/update", json=payload_update)
        if 200 <= request.status_code < 300:
            return True
        else:
            return False

    def load_json_facts(self, db: Session, file: SpooledTemporaryFile, user: models.User) -> str:
        count = 0
        json_data = json.load(file)
        for fact_obj in json_data:
            self.create_fact(db, fact_obj, user, False)
            count += 1
        logger.info(f"{count} facts loaded from txt file")

    def load_txt_facts(self, db: Session, file: SpooledTemporaryFile, user: models.User,
                       props: schemas.FileProps) -> str:
        count = 0
        with file as f:
            df = pandas.read_csv(f, sep=props.delimeter, names=props.headers, index_col=False)
            for index, fact_obj in df.iterrows():
                if schemas.Field.deck in props.headers and not pandas.isna(fact_obj[schemas.Field.deck]):
                    deck_id = crud.deck.find_or_create(db, proposed_deck=fact_obj["deck"], user=user).id
                else:
                    deck_id = props.default_deck.id
                fact_in = schemas.FactCreate(
                    text=fact_obj[schemas.Field.text],
                    answer=fact_obj[schemas.Field.answer],
                    deck_id=deck_id,
                    answer_lines=[fact_obj[schemas.Field.answer]],
                    extra={"type": "uploaded"}
                )
                if schemas.Field.identifier in props.headers and not pandas.isna(fact_obj[schemas.Field.identifier]):
                    fact_in.identifier = fact_obj[schemas.Field.identifier]
                if schemas.Field.category in props.headers and not pandas.isna(fact_obj[schemas.Field.category]):
                    fact_in.identifier = fact_obj[schemas.Field.category]
                crud.fact.create_with_owner(db, obj_in=fact_in, user=user)
                count += 1
        logger.info(f"{count} facts loaded from txt file")

    def create_fact(self, db: Session, fact_obj: Any, user: models.User, public: bool):
        deck = crud.deck.find_or_create(db, proposed_deck=fact_obj["deck"], user=user, public=public)
        fact_in = schemas.FactCreate(
            text=fact_obj["text"],
            answer=fact_obj["answer"],
            deck_id=deck.id,
            answer_lines=fact_obj["answer_lines"],
            identifier=fact_obj["identifier"],
            category=fact_obj["category"],
            extra=fact_obj["extra"]
        )
        crud.fact.create_with_owner(db, obj_in=fact_in, user=user)


fact = CRUDFact(models.Fact)
