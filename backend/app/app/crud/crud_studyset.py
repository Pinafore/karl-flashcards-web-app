from random import shuffle
from typing import List, Optional, Union, Any, Tuple
import time
import math
from itertools import islice
from app.schemas.target_window import TargetWindow

import requests
import json

from app import crud, models, schemas
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.config import settings
import requests
from pytz import timezone
import pytz
from datetime import datetime
from sentry_sdk import capture_exception
from sqlalchemy.sql.expression import true
from sqlalchemy import and_, false, func, not_, or_
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from fastapi import HTTPException
from sentry_sdk import capture_exception
from app.utils.utils import logger, log_time, time_it, TimeContainer


class CRUDStudySet(CRUDBase[models.StudySet, schemas.StudySetCreate, schemas.StudySetUpdate]):
    # def create(self, db: Session, *, obj_in: schemas.StudySetCreate):
    #     db_obj = self.create(db, obj_in=obj_in.)
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj

    def create_with_facts(self, db: Session, *, obj_in: schemas.StudySetCreate, facts: Optional[List[models.Fact]],
                          decks: Optional[List[models.Deck]]) -> models.StudySet:
        logger.info(f"Creating with facts {obj_in}")
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

    def mark_retired(self, db: Session, db_obj: models.StudySet) -> None:
        db_obj.retired = True
        db.commit()

    def retire_or_return_active_set(self,
                      db: Session,
                      *,
                      user: models.User,
                      force_new: bool) -> Optional[models.StudySet]:
        # Does not return study sets that are expired or completed
        uncompleted_last_set = self.find_active_study_set(db, user)
        
        if uncompleted_last_set:
            if force_new and uncompleted_last_set.set_type == schemas.SetType.normal:
                # Marks the study set as completed even though it hasn't been finished, due to override
                self.mark_retired(db, db_obj=uncompleted_last_set)
            else:
                # Return the uncompleted last set if it exists and the user has not force-requested a new set
                return uncompleted_last_set
        return None

    # Does not return study sets that are expired or completed
    def find_active_study_set(self, db: Session, user: models.User) -> Optional[models.StudySet]:
        studyset: models.StudySet = db.query(models.StudySet).filter(models.StudySet.user_id == user.id).order_by(
            models.StudySet.id.desc()).first()
        if studyset and not (studyset.expired or studyset.completed):
            return studyset
        else:
            return None
        
    def check_if_in_test_mode(self,
                      db: Session,
                      *,
                      user: models.User,
                      ) -> Union[
        bool, requests.exceptions.RequestException, json.decoder.JSONDecodeError]:

        # Determine study state
        test_deck, num_test_deck_studies = crud.deck.get_current_user_test_deck(db=db, user=user)

        active_set = self.retire_or_return_active_set(db, user=user, force_new=False)

        # Adjust count when current set has not been completed
        if active_set and active_set.set_type in {schemas.SetType.test, schemas.SetType.post_test}:
            return True

        if num_test_deck_studies > settings.POST_TEST_TRIGGER + 1:
            raise HTTPException(status_code=576, detail="USER STUDIED MORE TEST DECKS THAN THEY SHOULD HAVE")
        elif num_test_deck_studies == settings.POST_TEST_TRIGGER + 1: # all done with test mode, resume normal study
            next_set_type = schemas.SetType.normal
        elif test_deck is None:
            raise HTTPException(status_code=576, detail="TEST ID WAS NONE?")
        else:
            next_set_type = self.check_next_set_type(db, user=user, test_deck=test_deck, num_test_deck_studies=num_test_deck_studies)
        logger.info(f"Test set: {next_set_type}")

        print(f"\n\nTest set: {next_set_type}\n\n")

        return next_set_type in {schemas.SetType.test, schemas.SetType.post_test}

    def get_study_set(self,
                      db: Session,
                      *,
                      user: models.User,
                      deck_ids: List[int] = None,
                      return_limit: Optional[int] = None,
                      send_limit: Optional[int] = 150,
                      force_new: bool,
                      is_resume: Optional[bool] = None,
                      ) -> Union[
        models.StudySet, requests.exceptions.RequestException, json.decoder.JSONDecodeError]:
        crud.deck.check_for_test_deck_ids(db=db, deck_ids=deck_ids)
        decks = crud.deck.get_user_decks_given_ids(db=db, user=user, deck_ids=deck_ids)

        # Determine study state
        test_deck, num_test_deck_studies = crud.deck.get_current_user_test_deck(db=db, user=user)

        active_set = self.retire_or_return_active_set(db, user=user, force_new=force_new)
        if active_set and (is_resume or active_set.set_type in {schemas.SetType.test, schemas.SetType.post_test}): # finish the set the user is currently studying if they hit resume, or its test mode
            return active_set

        print('\n\nNum Test Studies:', num_test_deck_studies)

        if num_test_deck_studies > settings.POST_TEST_TRIGGER + 1:
            raise HTTPException(status_code=576, detail="USER STUDIED MORE TEST DECKS THAN THEY SHOULD HAVE")
        elif num_test_deck_studies == settings.POST_TEST_TRIGGER + 1: # all done with test mode, resume normal study
            next_set_type = schemas.SetType.normal
        elif test_deck is None:
            raise HTTPException(status_code=576, detail="TEST ID WAS NONE?")
        else:
            next_set_type = self.check_next_set_type(db, user=user, test_deck=test_deck, num_test_deck_studies=num_test_deck_studies)
        logger.info(f"Test set: {next_set_type}")

        if next_set_type == schemas.SetType.test:
            if active_set and active_set.set_type == schemas.SetType.test:
                return active_set
            db_obj = self.create_new_test_study_set(db, user=user, test_deck=test_deck)
        elif next_set_type == schemas.SetType.post_test:
            if active_set and active_set.set_type == schemas.SetType.post_test:
                return active_set
            db_obj = self.create_post_test_study_set(db, user=user, test_deck=test_deck)
        elif next_set_type == schemas.SetType.normal:
            if active_set:
                return active_set
            db_obj = self.create_new_study_set(db, user=user, decks=decks, deck_ids=deck_ids, return_limit=return_limit,
                                                   send_limit=send_limit)
            
        else:
            raise HTTPException(status_code=672, detail=f"Unknown study set type: {next_set_type}")
    
        return db_obj


    def create_scheduler_query(self, db: Session, facts: List[models.Fact], user: models.User, repetition_model: schemas.Repetition, set_type: schemas.SetType,
            test_mode: Optional[int] = None):
        # TODO: Remove recall_target when confirmed possible!
        scheduler_query = schemas.SchedulerQuery(facts=[schemas.KarlFactV2.from_orm(fact) for fact in facts],
                                                 env=settings.ENVIRONMENT,
                                                 repetition_model=repetition_model,
                                                 set_type=set_type,
                                                 user_id=user.id,
                                                 recall_target=TargetWindow(target_window_lowest=0, 
                                                 target_window_highest=1, target=.85),
                                                 test_mode=test_mode)
        return scheduler_query
    
    def get_overriden_scheduler(self, db: Session, user: models.User, test_deck_id: int):
        # return the overriden scheduler for the user, if in test mode
        query = (db.query(models.User_Deck)
                                        .filter(models.User_Deck.owner_id == user.id)
                                        .filter(models.User_Deck.deck_id == test_deck_id))
        user_deck: models.User_Deck = query.first()
        return user_deck.repetition_model_override

    def create_new_test_study_set(self, db: Session, *, user: models.User, return_limit: int = settings.TEST_MODE_PER_ROUND, test_deck: models.Deck) -> models.StudySet:
        # Get facts that have not been studied before
        test_deck_id = test_deck.id
        if test_deck is None:
            raise HTTPException(560, detail="Test Deck Not Found")
        logger.info(f"Test deck id: {test_deck.id}")
        study_set = self.create_new_study_set(db=db, user=user, decks=[test_deck], deck_ids=[test_deck_id], return_limit=return_limit, setType=schemas.SetType.test)
        return study_set
    
    def create_post_test_study_set(self, db: Session, *, user: models.User, test_deck: models.Deck) -> models.StudySet:
        facts = test_deck.facts
        study_set = self.create_with_facts(db, obj_in=schemas.StudySetCreate(repetition_model=user.repetition_model, user_id=user.id, set_type=schemas.SetType.post_test),
                                        decks=[test_deck],
                                        facts=facts)
        details = {
                "post_test": True,
                "set_type": schemas.SetType.post_test
            }
        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            log_type=schemas.Log.get_post_test_facts, # Update to dynamically get schemas.Log.get_test_facts
            details=details,
        )
        crud.history.create(db=db, obj_in=history_in)
        db.commit()
        
        return study_set

    def create_new_study_set(
            self,
            db: Session,
            *,
            user: models.User,
            decks: List[models.Deck],
            deck_ids: List[int] = None,
            return_limit: Optional[int] = None,
            send_limit: Optional[int] = None,
            repetition_model: Optional[schemas.Repetition] = None,
            setType: schemas.SetType = schemas.SetType.normal,
    ) -> Tuple[List[models.Fact], str]:

        print('\n\nCreating new study set:', repetition_model, user.repetition_model)
        print('Deck IDs:', deck_ids)

        show_hidden = setType == schemas.SetType.post_test or setType == schemas.SetType.test
        filters = schemas.FactSearch(deck_ids=deck_ids, limit=send_limit, studyable=True, show_hidden=show_hidden)
        base_facts_query = crud.fact.build_facts_query(db=db, user=user, filters=filters)
        #logger.info(base_facts_query)
        if repetition_model is None:
            if show_hidden:
                overriden_model = self.get_overriden_scheduler(db, user, deck_ids[0])
                repetition_model = overriden_model
            else:
                repetition_model = user.repetition_model

        print('Final repetition model:', repetition_model)
        
        if repetition_model == schemas.Repetition.karl:
            eligible_facts = crud.fact.get_eligible_facts(query=base_facts_query, limit=send_limit, randomize=True)
        else:
            eligible_old_facts_query = crud.helper.filter_only_reviewed_facts(query=base_facts_query, user_id=user.id, log_type=schemas.Log.study)
            print('Num old facts:', setType, len(eligible_old_facts_query.all()), '\n')
            eligible_facts = crud.fact.get_eligible_facts(query=eligible_old_facts_query, limit=send_limit, randomize=True)

        logger.info(f"return limit {return_limit}")
        time_container = TimeContainer()
        with log_time(description="Scheduler query creation", container=time_container, label="eligible_fact_time"):
            # TODO: ADD Post test
            if setType == schemas.SetType.test:
                test_deck_id = deck_ids[0]
                schedule_query = self.create_scheduler_query(db=db, facts=eligible_facts, user=user, repetition_model=repetition_model, set_type=setType, test_mode=test_deck_id)
            else:
                schedule_query = self.create_scheduler_query(db=db, facts=eligible_facts, user=user, set_type=setType, repetition_model=repetition_model)
        try:
            logger.info(schedule_query.dict())
            with log_time(description="Scheduler querying", container=time_container, label="scheduler_query_time"):
                scheduler_response = requests.post(settings.INTERFACE + "api/karl/schedule_v3", json=schedule_query.dict())
                response_json = scheduler_response.json()
            logger.info(f"response request: {scheduler_response.request}")
            card_order = response_json["order"]
            rationale = response_json["rationale"]
            debug_id = response_json["debug_id"]

            if rationale == "<p>no fact received</p>":
                logger.info("No Facts Received")
                raise HTTPException(status_code=558, detail="No Facts Received From Scheduler")
            # Generator idea adapted from https://stackoverflow.com/a/42393595
            order_generator = (eligible_facts[x] for x in card_order)
            facts = list(islice(order_generator, return_limit))
            logger.info("facts: " + str(facts))
            logger.info("debug id: " + debug_id)

            old_facts = facts
            if repetition_model != schemas.Repetition.karl:
                eligible_new_facts_query = crud.helper.filter_only_new_facts(query=base_facts_query, user_id=user.id, log_type=schemas.Log.study)
                new_facts = crud.fact.get_eligible_facts(query=eligible_new_facts_query, limit=return_limit, randomize=True)
                logger.info("new facts: " + str(new_facts))
                facts = crud.helper.combine_two_fact_sets(new_facts=new_facts, old_facts=facts, return_limit=return_limit)
            logger.info(f"Study set created of type {setType}")
            study_set_create = schemas.StudySetCreate(repetition_model=repetition_model, user_id=user.id, debug_id=debug_id, set_type=setType)
            logger.info(f"Study set create: {study_set_create}")
            study_set = self.create_with_facts(db, obj_in=study_set_create,
                                        decks=decks,
                                        facts=facts)
            details = {
                "study_system": repetition_model,
                "first_fact": schemas.Fact.from_orm(facts[0]) if len(facts) != 0 else "empty",
                "facts": [schemas.Fact.from_orm(fact) for fact in facts],
                "first_review_fact": schemas.Fact.from_orm(old_facts[0]) if len(old_facts) != 0 else "empty",
                "reviewfacts": [schemas.Fact.from_orm(fact) for fact in old_facts],
                "debug_id": debug_id,
                "recall_target": user.recall_target,
                "set_type": schemas.SetType.post_test
            }
            details.update(time_container.elapsed_times)
            history_in = schemas.HistoryCreate(
                time=datetime.now(timezone('UTC')).isoformat(),
                user_id=user.id,
                log_type=schemas.Log.get_test_facts if setType == schemas.SetType.test else schemas.Log.get_facts, # Update to dynamically get schemas.Log.get_test_facts
                details=details,
            )
            crud.history.create(db=db, obj_in=history_in)
            db.commit()
            
            print('\n\nDECK IDs:', deck_ids, '\n\n')

            return study_set
        except requests.exceptions.RequestException as e:
            capture_exception(e)
            raise HTTPException(status_code=555, detail="Connection to scheduler is down")
        except json.decoder.JSONDecodeError as e:
            capture_exception(e)
            raise HTTPException(status_code=556, detail="Scheduler malfunction")
    
    def find_last_test_or_post_test_set(self, db: Session, user: models.User) -> Optional[models.StudySet]:
        # Don't show 'retired' test set cards, which come from deleted test mode decks.
        studyset: models.StudySet = (db.query(models.StudySet)
                                     .filter(models.StudySet.user_id == user.id)
                                     .filter(or_(models.StudySet.is_test == true(), models.StudySet.is_post_test == true()))
                                     .filter(or_(models.StudySet.retired == None,
                                                  models.StudySet.retired == false()))
                                                  .order_by(models.StudySet.id.desc()).first())
        return studyset
    
    def completed_sets(self, db: Session, user: models.User) -> Optional[int]:
        logger.info("completed sets func: " + str(db.query(models.StudySet).filter(models.StudySet.user_id == user.id).count()))
        return db.query(models.StudySet).filter(models.StudySet.user_id == user.id).filter(models.StudySet.completed == true()).count()

    def sets_since_last_test(self, db: Session, last_test_set: models.studyset, user: models.User) -> Optional[int]:
        return db.query(models.StudySet).filter(models.StudySet.user_id == user.id).filter(models.StudySet.completed == true()).filter(models.StudySet.id > last_test_set.id).count()

    def get_deck_studyset_count(self, db: Session, user: models.User, deck: models.Deck) -> Optional[int]:
        return db.query(models.Session_Deck).options(joinedload(models.Session_Deck.studyset)).filter(models.Session_Deck.deck == deck, models.Session_Deck.studyset.has(user=user)).count()
    
    def update_session_facts(self, db: Session, schedules: List[schemas.Schedule], user: models.User,
                             studyset_id: int) -> Any:
        studyset = self.get(db=db, id=studyset_id)
        if not studyset:
            raise HTTPException(status_code=404, detail="Studyset not found")
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

        # Mark study set as completed if it is, and mark user deck completed if study set is a post-test
        # TODO: CHECK if this actually deprecated now?
        studyset_completed = studyset.completed
        if studyset.set_type == schemas.SetType.post_test and studyset.completed:
            crud.deck.mark_user_deck_completed(db=db, db_obj=studyset.decks[0], user=user)
        return schemas.ScheduleResponse(session_complete=studyset_completed)

    def record_study(
            self, db: Session, *, user: models.User, session_fact: models.Session_Fact, schedule: schemas.Schedule
    ) -> models.History:
        try:
            response = schedule.response
            date_studied = datetime.now(timezone('UTC')).isoformat()
            debug_id = session_fact.studyset.debug_id
            set_type = session_fact.studyset.set_type

            repetition_model = user.repetition_model
            if set_type in {schemas.SetType.test, schemas.SetType.post_test}:
                deck_id = session_fact.fact.deck_id
                repetition_model = self.get_overriden_scheduler(db, user, deck_id)

            details = {
                "studyset_id": session_fact.studyset_id,
                "study_system": repetition_model,
                "typed": schedule.typed,
                "response": schedule.response,
                "debug_id": debug_id,
                "recall_target": user.recall_target,
                "recommendation": schedule.recommendation,
                "set_type": set_type
            }
            if schedule.elapsed_seconds_text:
                details["elapsed_seconds_text"] = schedule.elapsed_seconds_text
                details["elapsed_seconds_answer"] = schedule.elapsed_seconds_answer
            else:
                details["elapsed_milliseconds_text"] = schedule.elapsed_milliseconds_text
                details["elapsed_milliseconds_answer"] = schedule.elapsed_milliseconds_answer
            fact = session_fact.fact
             # Could refactor into session fact field
            history_in = schemas.HistoryCreate(
                    time=date_studied,
                    user_id=user.id,
                    fact_id=fact.fact_id,
                    log_type=schemas.Log.study,
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
                test_mode=fact.deck_id if set_type in {schemas.SetType.test, schemas.SetType.post_test} else None,
                set_type=set_type,
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

    def check_next_set_type(
            self, db: Session, *, user: models.User, test_deck: models.Deck, num_test_deck_studies: int
    ) -> bool:
        logger.info("Checking in Test Mode")
        last_test_set = studyset.find_last_test_or_post_test_set(db, user)
        if last_test_set:
            logger.info("Last test Study set: " + str(last_test_set.id))
        else:
            logger.info("No test set found")
        logger.info("Studied facts: " + str(crud.user.studied_facts(db, user)))
        if last_test_set is None:
            logger.info("completed sets checking: " + str(studyset.completed_sets(db, user)))
            return schemas.SetType.test

        # Make current_time offset-aware using the same timezone
        current_time = datetime.now(timezone('UTC'))
        time_difference = current_time - last_test_set.create_date
        logger.info(f"Time difference between tests: {time_difference}")
        
        #if time_difference <= timedelta(seconds=5):
        if time_difference <= timedelta(hours=settings.TEST_MODE_NUM_HOURS):
            if last_test_set.completed:
                return schemas.SetType.normal
            else:
                return last_test_set.set_type
                #raise HTTPException(status_code=568, detail="Last test incomplete but not picked")
        else:
            # Currently, we don't have easy ways to distinguish between learning/review/relearning stages in logs. Instead, we do post test by # sets with current test set
            print('\n\nTEST SET COUNT:', num_test_deck_studies, '\n\n')
            if num_test_deck_studies >= settings.POST_TEST_TRIGGER:
                logger.info("GETTING TO POST TEST")
                return schemas.SetType.post_test
            else:
                logger.info("GETTING TO TEST")
                return schemas.SetType.test

studyset = CRUDStudySet(models.StudySet)
