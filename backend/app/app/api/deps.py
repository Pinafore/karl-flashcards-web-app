from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

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
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


class Paginate:
    def __init__(self, skip: int = None, limit: int = None):
        self.skip = skip
        self.limit = limit

class CheckFactPerms():
    def __init__(self, fact_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
        fact = crud.fact.get(db=db, id=fact_id)
        if not fact:
            raise HTTPException(status_code=404, detail="Fact not found")
        if not crud.user.is_superuser(current_user) and (fact.user_id != current_user.id):
            raise HTTPException(status_code=401, detail="Not enough permissions")
        self.fact = fact
        self.db = db
        self.current_user = current_user
        self.fact_id = fact_id

# def check_fact_and_perms(fact_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)) -> models.Fact:
#     fact = crud.fact.get(db=db, id=fact_id)
#     if not fact:
#         raise HTTPException(status_code=404, detail="Fact not found")
#     if not crud.user.is_superuser(current_user) and (fact.user_id != current_user.id):
#         raise HTTPException(status_code=401, detail="Not enough permissions")
#     return fact
