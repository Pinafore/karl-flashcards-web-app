from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pytz import timezone
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app import crud, models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from app.core.config import settings
from app.utils.utils import log_time

router = APIRouter()


@router.get("/", response_model=schemas.FactBrowse)
def read_facts(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        all: Optional[str] = None,
        text: Optional[str] = None,
        answer: Optional[str] = None,
        category: Optional[str] = None,
        identifier: Optional[str] = None,
        deck_ids: Optional[List[int]] = Query(None),
        deck_id: Optional[int] = None,
        marked: Optional[bool] = None,
        suspended: Optional[bool] = None,
        reported: Optional[bool] = None,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve facts.
    """
    if limit > 1000:
        raise HTTPException(status_code=445, detail="Too many facts requested. Please limit to <1000 facts.")
    crud.deck.check_for_test_deck_ids(db=db, deck_ids=deck_ids)
    # This ensures the user doesn't search for facts that they don't have access to
    decks = crud.deck.get_user_decks_given_ids(db=db, user=current_user, deck_ids=deck_ids)

    if suspended and reported:
        studyable = True
    else:
        studyable = False
    search = schemas.FactSearch(all=all,
                                text=text,
                                answer=answer,
                                category=category,
                                identifier=identifier,
                                deck_ids=deck_ids,
                                deck_id=deck_id,
                                marked=marked,
                                suspended=suspended,
                                reported=reported,
                                studyable=studyable,
                                skip=skip,
                                limit=limit
                                )
    query = crud.fact.build_facts_query(db=db, user=current_user, filters=search)
    facts = crud.fact.get_eligible_facts(query=query, skip=skip, limit=limit)
    total = len(facts)
    if total == limit:
        total = crud.fact.count_eligible_facts(query=query)

    with log_time("Add permissions to facts"):
        new_facts: List[schemas.Fact] = []
        for fact in facts:
            new_facts.append(crud.fact.get_schema_with_perm(db_obj=fact, user=current_user))

    fact_browser = schemas.FactBrowse(facts=new_facts, total=total)
    details = search.dict()
    details["study_system"] = current_user.repetition_model
    history_in = schemas.HistoryCreate(
        time=datetime.now(timezone('UTC')).isoformat(),
        user_id=current_user.id,
        log_type=schemas.Log.browser,
        details=details
    )
    crud.history.create(db=db, obj_in=history_in)
    return fact_browser


@router.post("/", response_model=schemas.Fact)
def create_fact(
        *,
        db: Session = Depends(deps.get_db),
        fact_in: schemas.FactCreate,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new fact.
    """
    fact = crud.fact.create_with_owner(db=db, obj_in=fact_in, user=current_user)
    return fact


@router.post("/upload/txt", response_model=bool)
def create_facts_txt(
        *,
        db: Session = Depends(deps.get_db),
        upload_file: UploadFile = File(...),
        deck_id: int = Form(...),
        headers: List[schemas.Field] = Query([schemas.Field.text, schemas.Field.answer]),
        delimeter: str = Form("\t"),
        background_tasks: BackgroundTasks,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Upload a txt/tsv/csv file with facts
    """
    if "text/plain" == upload_file.content_type or "text/csv" == upload_file.content_type:
        deck = crud.deck.get(db=db, id=deck_id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")
        if deck not in current_user.decks:
            raise HTTPException(status_code=401, detail="User does not possess the specified deck")
        props = schemas.FileProps(default_deck=deck, delimeter=delimeter, headers=headers)
        background_tasks.add_task(crud.fact.load_txt_facts, db=db, file=upload_file.file, user=current_user,
                                  props=props)
    else:
        raise HTTPException(status_code=423, detail="This file type is unsupported")

    return True


@router.post("/upload/json", response_model=bool)
def create_facts_json(
        *,
        db: Session = Depends(deps.get_db),
        upload_file: UploadFile = File(...),
        background_tasks: BackgroundTasks,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Upload a json file with facts
    """

    if "application/json" == upload_file.content_type:
        background_tasks.add_task(crud.fact.load_json_facts, db=db, file=upload_file.file, user=current_user)
    else:
        raise HTTPException(status_code=423, detail="This file type is unsupported")

    return True


@router.put("/preloaded", response_model=bool)
def update_preloaded_facts(
        *,
        current_user: models.User = Depends(deps.get_current_active_superuser),  # noqa
) -> Any:
    """
    Update preloaded facts.
    """
    celery_app.send_task("app.worker.clean_up_preloaded_facts")
    return True


@router.put("/test-mode", response_model=bool)
def create_test_mode_facts(
        *,
        current_user: models.User = Depends(deps.get_current_active_superuser),  # noqa
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Update preloaded facts.
    """
    celery_app.send_task("app.worker.create_test_mode_facts", kwargs={"filename": settings.TEST_MODE_FILE})
    return True


@router.put("/{fact_id}", response_model=schemas.Fact)
def update_fact(
        *,
        fact_in: schemas.FactUpdate,
        perms: deps.OwnerFactPerms = Depends(),
) -> Any:
    """
    Update a fact.
    """
    details = {
        "old_fact": perms.fact.__dict__,
        "fact_update": fact_in.dict(),
    }

    fact = crud.fact.update(db=perms.db, db_obj=perms.fact, obj_in=fact_in)

    history_in = schemas.HistoryCreate(
        time=datetime.now(timezone('UTC')).isoformat(),
        user_id=perms.current_user.id,
        log_type=schemas.Log.update_fact,
        details=details

    )
    crud.history.create(db=perms.db, obj_in=history_in)
    return fact


@router.get("/{fact_id}", response_model=schemas.Fact)
def read_fact(
        *,
        perms: deps.CheckFactPerms = Depends(),
) -> Any:
    """
    Get fact by ID.
    """
    return perms.fact


@router.delete("/{fact_id}", response_model=schemas.Fact)
def delete_fact(
        *,
        perms: deps.CheckFactPerms = Depends(),
) -> Any:
    """
    Delete a fact.
    """
    if perms.current_user in perms.fact.markers:
        fact = crud.fact.undo_remove(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    else:
        fact = crud.fact.remove(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    return fact


@router.put("/suspend/{fact_id}", response_model=schemas.Fact)
def suspend_fact(
        *,
        perms: deps.CheckFactPerms = Depends(),
) -> Any:
    """
    Suspend a fact.
    """
    if perms.current_user in perms.fact.markers:
        fact = crud.fact.undo_suspend(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    else:
        fact = crud.fact.suspend(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    return fact


@router.put("/report/{fact_id}", response_model=schemas.Fact)
def report_fact(
        *,
        perms: deps.CheckFactPerms = Depends(),
        suggestion: schemas.FactToReport,
) -> Any:
    """
    Report or undo report of a fact.
    """
    if perms.current_user in perms.fact.reporters:
        crud.fact.undo_report(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    fact = crud.fact.report(db=perms.db, db_obj=perms.fact, user=perms.current_user, suggestion=suggestion)
    return fact


@router.delete("/report/{fact_id}", response_model=schemas.Fact)
def clear_report_fact(
        *,
        perms: deps.CheckFactPerms = Depends(),
) -> Any:
    """
    Report or undo report of a fact.
    """
    if perms.current_user in perms.fact.reporters:
        fact = crud.fact.undo_report(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    else:
        raise HTTPException(status_code=448, detail="User has not previously reported this fact")
    return fact


@router.put("/mark/{fact_id}", response_model=schemas.Fact)
def mark_fact(
        *,
        perms: deps.CheckFactPerms = Depends(),
) -> Any:
    """
    Mark a fact.
    """
    if perms.current_user in perms.fact.markers:
        fact = crud.fact.undo_mark(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    else:
        fact = crud.fact.mark(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    return fact


@router.delete("/report/all/{fact_id}", response_model=schemas.Fact)
def clear_reports(
        *,
        perms: deps.CheckFactPerms = Depends(),
) -> Any:
    """
    Clears a user's reports or supensions of a fact.
    """
    if crud.user.is_superuser(perms.current_user):
        fact = crud.fact.resolve_report(db=perms.db, user=perms.current_user, db_obj=perms.fact)
    return fact
