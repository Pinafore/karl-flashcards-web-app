from typing import Generator, Optional

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
        current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
        current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


class Paginate:
    def __init__(self, skip: Optional[int] = None, limit: Optional[int] = None):
        self.skip = skip
        self.limit = limit


class OwnerFactPerms:
    def __init__(self, fact_id: int, db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_active_user)):
        fact = crud.fact.get(db=db, id=fact_id)
        if not fact:
            raise HTTPException(status_code=404, detail="Fact not found")
        if not crud.user.is_superuser(current_user) and (fact.user_id != current_user.id):
            user_deck = (db.query(models.User_Deck)
                         .filter(models.User_Deck.owner_id == current_user.id)
                         .filter(models.User_Deck.deck_id == fact.deck_id)
                         .filter(models.User_Deck.permissions == schemas.Permission.owner)
                         .first())

            if not user_deck:
                raise HTTPException(status_code=401, detail="Not enough permissions")
        self.fact = fact
        self.db = db
        self.current_user = current_user
        self.fact_id = fact_id


class CheckFactPerms:
    def __init__(self, fact_id: int, db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_active_user)):
        fact = crud.fact.get(db=db, id=fact_id)
        if not fact:
            raise HTTPException(status_code=404, detail="Fact not found")
        if not crud.user.is_superuser(current_user) and fact.user_id != current_user.id:
            # If the user doesn't own this fact then the fact owner must be an owner of the fact's deck
            # in order for the fact to be viewable/actionable by the current user
            user_deck = (db.query(models.User_Deck)
                         .filter(models.User_Deck.owner_id == fact.user_id)
                         .filter(models.User_Deck.deck_id == fact.deck_id)
                         .filter(models.User_Deck.permissions == schemas.Permission.owner)
                         .first())

            if not user_deck:
                raise HTTPException(status_code=401, detail="Not enough permissions")
        self.fact = fact
        self.db = db
        self.current_user = current_user
        self.fact_id = fact_id
