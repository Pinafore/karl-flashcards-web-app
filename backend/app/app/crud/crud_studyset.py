import logging
from typing import List, Optional, Union

import requests
import json

from app import crud, models, schemas
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDStudySet(CRUDBase[models.StudySet, schemas.StudySetCreate, schemas.StudySetUpdate]):
    # def create(self, db: Session, *, obj_in: schemas.StudySetCreate):
    #     db_obj = self.create(db, obj_in=obj_in.)
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj

    def create_with_facts(self, db: Session, *, obj_in: schemas.StudySetCreate, facts: List[models.Fact],
                          decks: Optional[List[models.Deck]]):
        db_obj = self.create(db, obj_in=obj_in)
        db.refresh(db_obj)
        # Not append because facts and decks are lists
        db_obj.decks.extend(decks)
        db_obj.facts.extend(facts)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def assign_facts(self, db: Session, *, db_obj: models.StudySet, facts: List[models.Fact]) -> None:
        for fact in facts:
            self.assign_fact(db, db_obj=db_obj, fact=fact)

    def assign_fact(self, db: Session, *, db_obj: models.StudySet, fact: models.Fact) -> None:
        session_fact = models.Session_Fact(studyset_id=db_obj.id, fact_id=fact.fact_id)
        db.add(session_fact)
        db.commit()

    def get_study_set(self,
                      db: Session,
                      *,
                      user: models.User,
                      deck_ids: List[int] = None,
                      return_limit: Optional[int] = None,
                      send_limit: Optional[int] = 300,
                      ) -> Union[
        schemas.StudySet, requests.exceptions.RequestException, json.decoder.JSONDecodeError, HTTPException]:
        decks = []
        test_deck_id = crud.deck.get_test_deck_id(db=db, user=user)
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
        if uncompleted_last_set:
            return uncompleted_last_set
        is_test_mode = crud.user.test_mode_check(db, db_obj=user)
        logger.info("test mode: " + str(is_test_mode))
        if is_test_mode:
            facts = crud.fact.get_test_facts(db, user=user)
            decks = [crud.deck.get_create_test_deck(db, user)]
        else:
            facts = crud.fact.get_study_set_facts(db, user=user, deck_ids=deck_ids, return_limit=return_limit,
                                                  send_limit=send_limit)
        logger.info(facts)
        db_obj = self.create_with_facts(db, obj_in=schemas.StudySetCreate(is_test=is_test_mode, user_id=user.id),
                                        decks=decks,
                                        facts=facts)
        obj_out = schemas.StudySet.from_orm(db_obj)
        return obj_out

    def find_existing_study_set(self, db: Session, user: models.User) -> Optional[schemas.StudySet]:
        studyset: models.StudySet = db.query(models.StudySet).filter(models.StudySet.user_id == user.id).order_by(
            models.StudySet.id.desc()).first()
        if studyset and studyset.completed:
            return studyset
        else:
            return None


studyset = CRUDStudySet(models.StudySet)
