import logging
from datetime import datetime
from typing import Any, Dict, Optional, Union

from pytz import timezone

from app import crud
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas import Repetition, Log
from app.schemas.user import UserCreate, UserUpdate, SuperUserCreate, SuperUserUpdate
from app.schemas.history import HistoryCreate
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import sys

sys.setrecursionlimit(1500)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        model = Repetition.select_model() if obj_in.repetition_model is None else obj_in.repetition_model
        logger.info(model)
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            username=obj_in.username,
            is_active=obj_in.is_active,
            repetition_model=model
        )
        db.add(db_obj)
        db.commit()
        deck = crud.deck.get(db=db, id=1)
        crud.deck.assign_viewer(db=db, db_obj=deck, user=db_obj)
        db.refresh(db_obj)
        return db_obj

    def super_user_create(self, db: Session, *, obj_in: SuperUserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            username=obj_in.username,
            is_superuser=obj_in.is_superuser,
            is_active=obj_in.is_active,
            repetition_model=obj_in.repetition_model
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
        if obj_in.password:
            if update_data["password"]:
                hashed_password = get_password_hash(update_data["password"])
                del update_data["password"]
                update_data["hashed_password"] = hashed_password
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

    def reassign_schedulers(self, db: Session):
        all_users = db.query(self.model).all()
        for found_user in all_users:
            old_repetition = found_user.repetition_model
            found_user = crud.user.update(db, db_obj=found_user,
                                          obj_in=UserUpdate(repetition_model=Repetition.select_model()))
            history_in = HistoryCreate(
                time=datetime.now(timezone('UTC')),
                user_id=found_user.id,
                log_type=Log.reassign_model,
                details={"old_repetition_model": old_repetition, "new_repetition_model": found_user.repetition_model}
            )
            crud.history.create(db=db, obj_in=history_in)


user = CRUDUser(User)
