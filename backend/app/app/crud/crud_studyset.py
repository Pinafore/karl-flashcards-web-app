import logging
from typing import List, Optional, Union, Any, Tuple
import time
import math
from itertools import islice

import requests
import json

from app import crud, models, schemas
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.config import settings
import requests
from pytz import timezone
from datetime import datetime
from sentry_sdk import capture_exception
from sqlalchemy.sql.expression import true
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from fastapi import HTTPException
from sentry_sdk import capture_exception

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDStudySet(CRUDBase[models.StudySet, schemas.StudySetCreate, schemas.StudySetUpdate]):
    # def create(self, db: Session, *, obj_in: schemas.StudySetCreate):
    #     db_obj = self.create(db, obj_in=obj_in.)
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj

    def create_with_facts(self, db: Session, *, obj_in: schemas.StudySetCreate, facts: Optional[List[models.Fact]],
                          decks: Optional[List[models.Deck]]) -> models.StudySet:
        db_obj = self.create(db, obj_in=obj_in)
        db.refresh(db_obj)
        # Not append because facts and decks are lists
        if decks:
            db_obj.decks.extend(decks)
        if facts:
            db_obj.facts.extend(facts)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_session_fact(self, db: Session, *, db_obj: models.StudySet, fact: models.Fact) -> None:
        session_fact = models.Session_Fact(studyset_id=db_obj.id, fact_id=fact.fact_id)
        db.add(session_fact)
        db.commit()

    def mark_retired(self, db: Session, db_obj: models.StudySet) -> None:
        db_obj.retired = True
        db.commit()

    def get_study_set(self,
                      db: Session,
                      *,
                      user: models.User,
                      deck_ids: List[int] = None,
                      return_limit: Optional[int] = None,
                      send_limit: Optional[int] = 1000,
                      force_new: bool,
                      ) -> Union[
        models.StudySet, requests.exceptions.RequestException, json.decoder.JSONDecodeError, HTTPException]:
        decks = []
        test_deck_id = crud.deck.get_test_deck_id(db=db)
        if deck_ids is not None:
            if test_deck_id in deck_ids:
                return HTTPException(status_code=557, detail="This deck is currently unavailable")
            for deck_id in deck_ids:
                deck = crud.deck.get(db=db, id=deck_id)
                if not deck:
                    return HTTPException(status_code=404, detail="One or more of the specified decks does not exist")
                if user not in deck.users:
                    return HTTPException(status_code=450,
                                         detail="This user does not have the necessary permission to access one or more"
                                                " of the specified decks")
                decks.append(deck)
        uncompleted_last_set = self.find_existing_study_set(db, user)
        # Return the uncompleted last set if it exists and the user has not force-requested a new set
        in_test_mode = self.in_test_mode(db, user=user)
        if uncompleted_last_set:
            if force_new and not uncompleted_last_set.is_test:
                # Marks the study set as completed even though it hasn't been finished, due to override
                self.mark_retired(db, db_obj=uncompleted_last_set)
            else:
                return uncompleted_last_set
        if in_test_mode:
            db_obj = self.create_new_test_study_set(db, user=user)
        else:
            db_obj = self.create_new_study_set(db, user=user, decks=decks, deck_ids=deck_ids, return_limit=return_limit,
                                                   send_limit=send_limit)
        # db_obj = self.create_with_facts(db, obj_in=study_set_create,
        #                                 decks=decks,
        #                                 facts=facts)
        # db_obj = self.create_with_facts(db, obj_in=schemas.StudySetCreate(is_test=in_test_mode, user_id=user.id, debug_id=debug_id if debug_id else None),
        #                                 decks=decks,
        #                                 facts=facts)
        return db_obj

    def find_existing_study_set(self, db: Session, user: models.User) -> Optional[models.StudySet]:
        studyset: models.StudySet = db.query(models.StudySet).filter(models.StudySet.user_id == user.id).order_by(
            models.StudySet.id.desc()).first()
        if studyset and not (studyset.expired or studyset.completed):
            return studyset
        else:
            return None
    
    def create_new_test_study_set(self, db: Session, *, user: models.User, return_limit: int = settings.TEST_MODE_PER_ROUND) -> models.StudySet:
        # Get facts that have not been studied before
        logger.info(crud.deck.get_test_deck_id(db=db))
        test_deck_id = crud.deck.get_test_deck_id(db=db)
        if test_deck_id is None:
            raise HTTPException(560, detail="Test Deck ID Not Found")

        init_new_facts_query = db.query(models.Fact).filter(models.Fact.deck_id == test_deck_id)
        # TODO: Test func.random()
        new_facts_query = crud.helper.filter_only_new_facts(init_new_facts_query, user_id=user.id, log_type=schemas.Log.test_study)
        new_facts = crud.fact.get_eligible_facts(query=new_facts_query, limit=return_limit, randomize=True)
        logger.info("New facts:" + str(new_facts))

        # Get facts that have been previously studied before, but were answered incorrectly
        init_old_facts_query = db.query(models.Fact).filter(models.Fact.deck_id == test_deck_id)
        # TODO: Test func.random()
        old_facts_query = crud.helper.filter_only_incorrectly_reviewed_facts(query=init_old_facts_query, user_id=user.id, log_type=schemas.Log.test_study)
        old_facts = crud.fact.get_eligible_facts(query=old_facts_query, limit=return_limit, randomize=True)
        logger.info("Old facts:" + str(old_facts))

        facts = crud.helper.combine_two_fact_sets(random_facts=new_facts, old_facts=old_facts, return_limit=return_limit)

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            log_type=schemas.Log.get_test_facts,
            details={
                "recall_target": user.recall_target,
            }
        )
        crud.history.create(db=db, obj_in=history_in)
        test_deck = crud.deck.get_test_deck(db)
        decks = [test_deck] if test_deck is not None else []
        study_set = self.create_with_facts(db, obj_in=schemas.StudySetCreate(is_test=True, user_id=user.id),
                                        decks=decks,
                                        facts=facts)
        db.commit()
        return study_set

    def create_scheduler_query(self, facts: List[models.Fact], user: models.User):
        
        scheduler_query = schemas.SchedulerQuery(facts=[schemas.KarlFactV2.from_orm(fact) for fact in facts],
                                                 env=settings.ENVIRONMENT, repetition_model=user.repetition_model,
                                                 user_id=user.id,
                                                 recall_target=settings.RECALL_WINDOW)
        return scheduler_query

    def create_new_study_set(
            self,
            db: Session,
            *,
            user: models.User,
            decks: List[models.Deck],
            deck_ids: List[int] = None,
            return_limit: Optional[int] = None,
            send_limit: Optional[int] = None,
    ) -> Tuple[List[models.Fact], str]:
        filters = schemas.FactSearch(deck_ids=deck_ids, limit=send_limit, studyable=True)
        base_facts_query = crud.fact.build_facts_query(db=db, user=user, filters=filters)
        eligible_old_facts_query = crud.helper.filter_only_reviewed_facts(query=base_facts_query, user_id=user.id, log_type=schemas.Log.study)
        eligible_old_facts = crud.fact.get_eligible_facts(query=eligible_old_facts_query, limit=send_limit, randomize=True)
        # logger.info("eligible fact length: " + str(len(eligible_facts)))
        # if not eligible_facts:
        #     return []
        
        rev_karl_list_start = time.time()
        schedule_query = self.create_scheduler_query(facts=eligible_old_facts, user=user)
        eligible_fact_time = time.time() - rev_karl_list_start
        logger.info("scheduler query time: " + str(eligible_fact_time))

        logger.info("eligible old facts: " + str(eligible_old_facts))
        karl_query_start = time.time()
        try:
            # if statement is temporary only while the scheduler is crashing on empty arrays
            scheduler_response = requests.post(settings.INTERFACE + "api/karl/schedule_v2", json=schedule_query.dict())
            response_json = scheduler_response.json()
            card_order = response_json["order"]
            rationale = response_json["rationale"]
            debug_id = response_json["debug_id"]

            query_time = time.time() - karl_query_start
            logger.info(scheduler_response.request)
            logger.info("query time: " + str(query_time))

            if rationale == "<p>no fact received</p>":
                logger.info("No Facts Received")
                # raise HTTPException(status_code=558, detail="No Facts Received From Scheduler")
            # Generator idea adapted from https://stackoverflow.com/a/42393595
            order_generator = (eligible_old_facts[x] for x in card_order)  # eligible facts instead?
            old_facts = list(islice(order_generator, return_limit))
            logger.info("old facts: " + str(old_facts))
            logger.info("debug id: " + debug_id)
            
            random_facts = crud.fact.get_eligible_facts(query=base_facts_query, limit=return_limit, randomize=True)
            logger.info("new facts: " + str(random_facts))

            facts = crud.helper.combine_two_fact_sets(random_facts=random_facts, old_facts=old_facts, return_limit=return_limit)
            study_set = self.create_with_facts(db, obj_in=schemas.StudySetCreate(is_test=False, user_id=user.id, debug_id=debug_id),
                                        decks=decks,
                                        facts=facts)
                                        
            details = {
                "study_system": user.repetition_model,
                "first_fact": schemas.Fact.from_orm(facts[0]) if len(facts) != 0 else "empty",
                "facts": [schemas.Fact.from_orm(fact) for fact in facts],
                "first_review_fact": schemas.Fact.from_orm(old_facts[0]) if len(old_facts) != 0 else "empty",
                "reviewfacts": [schemas.Fact.from_orm(fact) for fact in old_facts],
                "eligible_fact_time": query_time,
                "scheduler_query_time": eligible_fact_time,
                "debug_id": debug_id,
                "recall_target": user.recall_target,
            }
            history_in = schemas.HistoryCreate(
                time=datetime.now(timezone('UTC')).isoformat(),
                user_id=user.id,
                log_type=schemas.Log.get_facts,
                details=details,
            )
            crud.history.create(db=db, obj_in=history_in)
            db.commit()
            
            return study_set
        except requests.exceptions.RequestException as e:
            capture_exception(e)
            raise HTTPException(status_code=555, detail="Connection to scheduler is down")
        except json.decoder.JSONDecodeError as e:
            capture_exception(e)
            raise HTTPException(status_code=556, detail="Scheduler malfunction")
    
    def find_last_test_set(self, db: Session, user: models.User) -> Optional[models.StudySet]:
        studyset: models.StudySet = db.query(models.StudySet).filter(models.StudySet.user_id == user.id).filter(models.StudySet.is_test == true()).order_by(
            models.StudySet.id.desc()).first()
        return studyset
    
    def completed_sets(self, db: Session, user: models.User) -> Optional[int]:
        return db.query(models.StudySet).filter(models.StudySet.user_id == user.id).filter(models.StudySet.completed == true()).count()

    def sets_since_last_test(self, db: Session, last_test_set: models.studyset, user: models.User) -> Optional[int]:
        return db.query(models.StudySet).filter(models.StudySet.user_id == user.id).filter(models.StudySet.completed == true()).filter(models.StudySet.id > last_test_set.id).count()

    
    def update_session_facts(self, db: Session, schedules: List[schemas.Schedule], user: models.User,
                             studyset_id: int) -> Any:
        studyset = self.get(db=db, id=studyset_id)
        if not studyset:
            raise HTTPException(status_code=404, detail="Studyset not found")
        # history_schemas = []
        for schedule in schedules:
            # fact = crud.fact.get(db=db, id=schedule.fact_id)
            session_fact = db.query(models.Session_Fact).filter(models.Session_Fact.studyset_id == studyset_id).filter(
                models.Session_Fact.fact_id == schedule.fact_id).first()
            if not session_fact:
                raise HTTPException(status_code=404, detail="Fact not found")
            history = self.record_study(db=db, user=user, session_fact=session_fact, schedule=schedule)

            # Mark that the session fact has been studied most recently here
            session_fact.history_id = history.id
            db.commit()
            # history_schemas.append(schemas.History.from_orm(history))
        return schemas.ScheduleResponse(session_complete=studyset.completed)

    def record_study(
            self, db: Session, *, user: models.User, session_fact: models.Session_Fact, schedule: schemas.Schedule
    ) -> models.History:
        try:
            response = schedule.response
            date_studied = datetime.now(timezone('UTC')).isoformat()
            debug_id = session_fact.studyset.debug_id
            details = {
                "studyset_id": session_fact.studyset_id,
                "study_system": user.repetition_model,
                "typed": schedule.typed,
                "response": schedule.response,
                "debug_id": debug_id,
                "recall_target": user.recall_target,
                "recommendation": schedule.recommendation
            }
            if schedule.elapsed_seconds_text:
                details["elapsed_seconds_text"] = schedule.elapsed_seconds_text
                details["elapsed_seconds_answer"] = schedule.elapsed_seconds_answer
            else:
                details["elapsed_milliseconds_text"] = schedule.elapsed_milliseconds_text
                details["elapsed_milliseconds_answer"] = schedule.elapsed_milliseconds_answer
            fact = session_fact.fact
            in_test_mode = fact.deck_id == crud.deck.get_test_deck_id(db) # Could refactor into session fact field
            history_in = schemas.HistoryCreate(
                    time=date_studied,
                    user_id=user.id,
                    fact_id=fact.fact_id,
                    log_type=schemas.Log.test_study if in_test_mode else schemas.Log.study,
                    correct=schedule.response,
                    details=details,
                )
            history = crud.history.create(db=db, obj_in=history_in)
            payload_update = schemas.UpdateRequestV2(
                user_id=user.id,
                fact_id=fact.fact_id,
                deck_name=fact.deck.title,
                deck_id=fact.deck_id,
                label=response,
                elapsed_milliseconds_text=schedule.elapsed_milliseconds_text,
                elapsed_milliseconds_answer=schedule.elapsed_milliseconds_answer,
                studyset_id=session_fact.studyset_id,
                history_id=history.id,
                answer=fact.answer,
                typed=schedule.typed,
                debug_id=debug_id,
                test_mode=in_test_mode,
                recommendation=schedule.recommendation,
                fact=schemas.KarlFactV2.from_orm(fact)).dict(exclude_unset=True)
            logger.info("payload update: " + str(payload_update))
            request = requests.post(settings.INTERFACE + "api/karl/update_v2", json=payload_update)
            logger.info("request content: " + str(request.content))
            if not 200 <= request.status_code < 300:
                raise HTTPException(status_code=556, detail="Scheduler malfunction")
            return history
        except requests.exceptions.RequestException as e:
            capture_exception(e)
            raise HTTPException(status_code=555, detail="Connection to scheduler is down")
        except json.decoder.JSONDecodeError as e:
            capture_exception(e)
            logger.info(e)
            raise HTTPException(status_code=556, detail="Scheduler malfunction")

    def in_test_mode(
            self, db: Session, *, user: models.User
    ) -> bool:
        study_set = studyset.find_last_test_set(db, user)
        if study_set is None:
            return studyset.completed_sets(db, user) > settings.TEST_MODE_FIRST_TRIGGER_SESSIONS
        # while this most recent test set could be expired, as long as it's not completed, user is still in test mode
        if not study_set.completed:
            return True
        over_days_trigger = (study_set.create_date + timedelta(days=settings.TEST_MODE_TRIGGER_DAYS) > datetime.now(timezone('UTC')))
        over_sessions_trigger = studyset.sets_since_last_test(db, last_test_set=study_set, user=user) > settings.TEST_MODE_TRIGGER_SESSIONS
        logger.info("In Test Mode: ")
        logger.info(over_days_trigger)
        logger.info(over_sessions_trigger)
        return over_days_trigger or over_sessions_trigger

studyset = CRUDStudySet(models.StudySet)
