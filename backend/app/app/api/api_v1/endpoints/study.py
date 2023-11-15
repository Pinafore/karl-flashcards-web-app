import json
from typing import Any, List, Optional

import requests
from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils import evaluate
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.utils.utils import logger
router = APIRouter()

@router.get("/test_mode", response_model=bool)
def check_if_in_test_mode(
        db: Session = Depends(deps.get_db),
        user_id: Optional[int] = None,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get next set of facts for review using user's schedule.
    Allows superusers to view anyone's future schedule.
    A user's deck ids can be provided for filtering.
    """
    
    if user_id:
        user = crud.user.get(db=db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not (crud.user.is_superuser(current_user) or user_id == current_user.id):
            raise HTTPException(status_code=400, detail="This user does not have the necessary permissions")
    else:
        user = current_user
    in_test_mode = crud.studyset.check_if_in_test_mode(db, user=user)
    return in_test_mode

@router.get("/", response_model=schemas.StudySet)
def get_next_set(
        db: Session = Depends(deps.get_db),
        user_id: Optional[int] = None,
        deck_ids: Optional[List[int]] = Query(None),
        force_new: bool = False,
        limit: int = 5,
        current_user: models.User = Depends(deps.get_current_active_user),
        is_resume: Optional[bool] = None
) -> Any:
    """
    Get next set of facts for review using user's schedule.
    Allows superusers to view anyone's future schedule.
    A user's deck ids can be provided for filtering.
    """
    if user_id:
        user = crud.user.get(db=db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not (crud.user.is_superuser(current_user) or user_id == current_user.id):
            raise HTTPException(status_code=400, detail="This user does not have the necessary permissions")
    else:
        user = current_user
    study_set = crud.studyset.get_study_set(db, user=user, deck_ids=deck_ids, return_limit=limit, force_new=force_new, is_resume=is_resume)
    print("\n\nSTUDY SET:", study_set.facts, len(study_set.facts), '\n\n')
    if isinstance(study_set, requests.exceptions.RequestException):
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
    if isinstance(study_set, json.decoder.JSONDecodeError):
        raise HTTPException(status_code=556, detail="Scheduler malfunction")
    return study_set


@router.put("/", response_model=schemas.ScheduleResponse)
def update_schedule_set(
        *,
        db: Session = Depends(deps.get_db),
        studyset_id: int = Query(...),
        facts_in: List[schemas.Schedule] = Body(...),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
        Updates the schedules of the returned fact set using the current user's assigned schedule
    """

    # successes = []
    response = crud.studyset.update_session_facts(db=db, schedules=facts_in, user=current_user, studyset_id=studyset_id)
    return response


@router.get("/evaluate", response_model=Optional[bool], summary="Evaluates accuracy of typed answer to the given fact")
def evaluate_answer(
        *,
        db: Session = Depends(deps.get_db),
        fact_id: int,
        typed: Optional[str] = None,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    fact = crud.fact.get(db=db, id=fact_id)
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")

    if typed is None:
        return False
    else:
        return evaluate.evaluate_answer(eval_fact=fact, typed=typed)


@router.get("/status", response_model=bool, summary="Checks status of connection to scheduler")
def scheduler_status() -> Any:
    try:
        r = requests.get(settings.INTERFACE + "api/karl/status")
        r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
        logger.info(e)
        raise HTTPException(status_code=555, detail="Connection to scheduler is down")
