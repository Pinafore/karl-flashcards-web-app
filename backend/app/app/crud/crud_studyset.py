import logging
from typing import List, Optional, Union, Any

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
from datetime import datetime, timedelta

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
            if force_new and not in_test_mode:
                self.mark_retired(db, db_obj=uncompleted_last_set)
            else:
                return uncompleted_last_set
        if in_test_mode:
            facts = crud.fact.get_test_facts(db, user=user)
            test_deck = crud.deck.get_test_deck(db)
            decks = [test_deck] if test_deck is not None else []
            debug_id = None
        else:
            facts, debug_id = crud.fact.get_ordered_schedule(db, user=user, deck_ids=deck_ids, return_limit=return_limit,
                                                   send_limit=send_limit)
        logger.info(facts)
        db_obj = self.create_with_facts(db, obj_in=schemas.StudySetCreate(is_test=in_test_mode, user_id=user.id, debug_id=debug_id if debug_id else None),
                                        decks=decks,
                                        facts=facts)
        db.commit()
        return db_obj

    def find_existing_study_set(self, db: Session, user: models.User) -> Optional[models.StudySet]:
        studyset: models.StudySet = db.query(models.StudySet).filter(models.StudySet.user_id == user.id).order_by(
            models.StudySet.id.desc()).first()
        if studyset and not (studyset.expired or studyset.completed):
            return studyset
        else:
            return None
    
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
                "study_system": user.repetition_model,
                "typed": schedule.typed,
                "response": schedule.response,
                "debug_id": debug_id,
                "recall_target": user.recall_target,
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
                test_mode=in_test_mode).dict(exclude_unset=True)
            logger.info(payload_update)
            request = requests.post(settings.INTERFACE + "api/karl/update_v2", json=payload_update)
            logger.info(request.content)
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
    ) -> models.History:
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
