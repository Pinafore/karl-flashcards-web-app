import json
from typing import Any, List, Optional

import requests
from fastapi import BackgroundTasks

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils.utils import send_new_account_email
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.utils import logger, log_time, time_it

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
        db: Session = Depends(deps.get_db),
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        current_user: models.User = Depends(deps.get_current_active_superuser),  # noqa
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.SuperUserCreate,
        current_user: models.User = Depends(deps.get_current_active_superuser),  # noqa
) -> Any:
    """
    Create new user.
    """

    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists in the system",
        )
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists in the system.",
        )
    user = crud.user.super_user_create(db, obj_in=user_in)
    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    if user_in.email:
        user = crud.user.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists in the system.",
            )

    if user_in.username:
        user = crud.user.get_by_username(db, username=user_in.username)
        if user:
            raise HTTPException(
                status_code=400,
                detail="A user with this username already exists in the system.",
            )

    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.UserWithStudySet)
def read_user_me(
        db: Session = Depends(deps.get_db),  # noqa
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=schemas.User)
def create_user_open(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )

    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists in the system",
        )
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists in the system.",
        )

    user_in = schemas.UserCreate(password=user_in.password, email=user_in.email, username=user_in.username)
    user = crud.user.create(db, obj_in=user_in)

    # if settings.EMAILS_ENABLED and user_in.email:
    #     send_new_account_email(
    #         email_to=user_in.email, username=user_in.username
    #     )
    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
        user_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/me/reassign", response_model=schemas.User)
def reassign_scheduler_me(
        *,
        db: Session = Depends(deps.get_db),
        repetition_model: Optional[schemas.Repetition],
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Reassign current user to assigned scheduler or create random new assignment
    """

    response = crud.user.reassign_scheduler(db=db, user=current_user, repetition_model=repetition_model)

    if isinstance(response, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(response, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")

    return response


@router.put("/{user_id}/reassign", response_model=schemas.User)
def reassign_scheduler(
        *,
        db: Session = Depends(deps.get_db),
        repetition_model: Optional[schemas.Repetition],
        user_id: int,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Reassign user to assigned scheduler or create random new assignment
    """

    user = crud.user.get(db, id=user_id)
    response = crud.user.reassign_scheduler(db=db, user=user, repetition_model=repetition_model)

    if isinstance(response, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(response, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")

    return response


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
        *,
        db: Session = Depends(deps.get_db),
        user_id: int,
        user_in: schemas.SuperUserUpdate,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.post("/bulk/reassign", response_model=bool)
def reassign_schedulers(
        *,
        db: Session = Depends(deps.get_db),
        background_tasks: BackgroundTasks,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Reassign the assigned scheduler for all users
    """

    background_tasks.add_task(crud.user.reassign_schedulers, db=db)

    return True

@router.post("/bulk/test", response_model=bool)
def assign_bulk_test_deck(
        *,
        db: Session = Depends(deps.get_db),
        background_tasks: BackgroundTasks,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Reassign the assigned scheduler for all users
    """

    background_tasks.add_task(crud.deck.assign_test_decks_to_all, db=db)

    return True