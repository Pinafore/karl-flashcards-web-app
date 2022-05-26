import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, List

import requests
import json
from pytz import timezone
from sentry_sdk import capture_exception

from app import crud
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.interface.reassignment import change_assignment
from app.interface.scheduler import set_user_settings
from app.models.user import User
from app.schemas import Repetition, Log
from app.schemas.user import UserCreate, UserUpdate, SuperUserCreate, SuperUserUpdate
from app.schemas.history import HistoryCreate
from sqlalchemy.orm import Session
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import sys



class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_all_with_status(self, db: Session, is_beta: Optional[bool] = False) -> List[User]:
        if is_beta:
            return db.query(User).all()
        else:
            return db.query(User).filter(User.beta_user == is_beta).all()

    def get_count(self, db: Session, is_beta: bool):
        return db.query(User).filter(User.beta_user == is_beta).count()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        model, assignment_method = self.assign_scheduler_to_new_user(db, obj_in)
        logger.info(model)
        logger.info(assignment_method)
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            username=obj_in.username,
            is_active=obj_in.is_active,
            repetition_model=model,
            recall_target=obj_in.recall_target,
        )
        db.add(db_obj)
        db.commit()
        deck = crud.deck.get(db=db, id=settings.DEFAULT_DECK_ID)
        crud.deck.assign_viewer(db=db, db_obj=deck, user=db_obj)
        db.refresh(db_obj)
        # Assign test
        crud.deck.assign_test_deck(db=db, user=db_obj)
        db.refresh(db_obj)
        change_assignment(user=db_obj, repetition_model=model)
        return db_obj

    def assign_scheduler_to_new_user(self, db: Session, obj_in: UserCreate) -> (Repetition, str):
        if obj_in.repetition_model:
            return obj_in.repetition_model, "assigned"
        if self.get_count(db, False) > 250:
            return Repetition.select_model(), "random"
        scheduler_counts = self.get_scheduler_counts(db, is_beta=False)
        keys_list = list(scheduler_counts.keys())
        params = [max(55 - scheduler_counts[i], 1) for i in keys_list]

        return keys_list[int(np.argmax(np.random.dirichlet(params)))], "dirichlet"

    def super_user_create(self, db: Session, *, obj_in: SuperUserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            username=obj_in.username,
            is_superuser=obj_in.is_superuser,
            is_active=obj_in.is_active,
            repetition_model=obj_in.repetition_model,
            beta_user=obj_in.beta_user,
            recall_target=obj_in.recall_target,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, SuperUserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if obj_in.password and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        if obj_in.recall_target and update_data["recall_target"]:
            set_user_settings(user=db_obj, new_settings=obj_in)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, username: str, password: str) -> Optional[User]:
        user1 = self.get_by_email(db, email=email)
        if not user1:
            user2 = self.get_by_username(db, username=username)
            if not user2:
                return None
            elif not verify_password(password, user2.hashed_password):
                return None
            else:
                return user2
        elif not verify_password(password, user1.hashed_password):
            return None
        else:
            return user1

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser

    def reassign_scheduler(self, db: Session, user: User, *,
                           repetition_model: Repetition = None) -> Union[
        User, requests.exceptions.RequestException, json.decoder.JSONDecodeError]:
        try:
            old_repetition = user.repetition_model
            new_repetition = repetition_model if repetition_model else Repetition.select_model()
            found_user = crud.user.update(db, db_obj=user,
                                          obj_in=UserUpdate(repetition_model=new_repetition))
            response = change_assignment(user=found_user, repetition_model=new_repetition)

            history_in = HistoryCreate(
                time=datetime.now(timezone('UTC')),
                user_id=found_user.id,
                log_type=Log.reassign_model,
                details={"old_repetition_model": old_repetition, "new_repetition_model": found_user.repetition_model}
            )
            crud.history.create(db=db, obj_in=history_in)
            return found_user
        except requests.exceptions.RequestException as e:
            capture_exception(e)
            return e
        except json.decoder.JSONDecodeError as e:
            capture_exception(e)
            return e

    def reassign_schedulers(self, db: Session):
        all_users = db.query(self.model).all()
        for found_user in all_users:
            old_repetition = found_user.repetition_model
            new_repetition = Repetition.select_model()
            found_user = crud.user.update(db, db_obj=found_user,
                                          obj_in=UserUpdate(repetition_model=new_repetition))
            change_assignment(user=found_user, repetition_model=new_repetition)
            history_in = HistoryCreate(
                time=datetime.now(timezone('UTC')),
                user_id=found_user.id,
                log_type=Log.reassign_model,
                details={"old_repetition_model": old_repetition, "new_repetition_model": found_user.repetition_model}
            )
            crud.history.create(db=db, obj_in=history_in)

    def get_scheduler_counts(self, db: Session, is_beta: Optional[bool] = None) -> {Repetition: int}:
        all_users = self.get_all_with_status(db, is_beta)

        scheduler_counts = {system: 0 for system in Repetition}
        for found_user in all_users:
            scheduler_counts[found_user.repetition_model] += 1  # type: ignore
        return scheduler_counts

    def make_current_users_beta_testers(self, db: Session):
        db.query(self.model).update({User.beta_user: True}, synchronize_session='evaluate')

    def test_mode_check(self, db: Session, db_obj: User) -> bool:
        return True
        if (db_obj.last_test_date is not None and
            db_obj.last_test_date + timedelta(days=7) > datetime.now(timezone('UTC'))) or \
                crud.history.get_user_study_count(user=db_obj) / settings.TEST_MODE_TRIGGER >= db_obj.next_test_mode:
            if crud.history.get_user_test_study_count(user=db_obj) >= \
                    db_obj.next_test_mode * settings.TEST_MODE_PER_ROUND:
                self.update(db, db_obj=db_obj,
                            obj_in=UserUpdate(next_test_mode=db_obj.next_test_mode + 1,
                                              last_test_date=datetime.now(timezone('UTC')).isoformat()))
            return True
        else:
            return False


user = CRUDUser(User)
