import logging
from typing import Any, Dict, Optional, Union

from app import crud
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, SuperUserCreate, SuperUserUpdate
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
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            username=obj_in.username,
            is_active=obj_in.is_active,
            repetition_model=obj_in.repetition_model
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


user = CRUDUser(User)
