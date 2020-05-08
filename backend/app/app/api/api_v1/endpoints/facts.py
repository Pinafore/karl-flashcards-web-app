from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Fact])
def read_facts(
    db: Session = Depends(deps.get_db),
    paginate: deps.Paginate = Depends(),
    text: Optional[str] = None,
    deck_ids: Optional[List[int]] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve facts.
    """
    search = schemas.Search(text=text, deck_ids=deck_ids)
    if crud.user.is_superuser(current_user):
        facts = crud.fact.get_multi_by_conditions(db=db, skip=paginate.skip, limit=paginate.limit, search=search)
    else:
        facts = crud.fact.get_multi_by_conditions(
            db=db, user=current_user, skip=paginate.skip, limit=paginate.limit, search=search
        )
    return facts


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


@router.put("/{fact_id}", response_model=schemas.Fact)
def update_fact(
    *,
    fact_in: schemas.FactUpdate,
    perms: deps.CheckFactPerms = Depends(),
) -> Any:
    """
    Update a fact.
    """
    fact = crud.fact.update(db=perms.db, db_obj=perms.fact, obj_in=fact_in)
    return fact


@router.get("/{fact_id}", response_model=schemas.Fact)
def read_fact(
    *,
    perms: deps.CheckFactPerms = Depends(),
    undo: bool = False,
) -> Any:
    """
    Get fact by ID.
    """
    return perms.fact


@router.delete("/{fact_id}", response_model=schemas.Fact)
def delete_fact(
    *,
    perms: deps.CheckFactPerms = Depends(),
    undo: bool = False,
) -> Any:
    """
    Delete a fact.
    """
    if undo:
        fact = crud.fact.undo_remove(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    else:
        fact = crud.fact.remove(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    return fact


@router.put("/suspend/{fact_id}", response_model=schemas.Fact)
def suspend_fact(
    *,
    perms: deps.CheckFactPerms = Depends(),
    undo: bool = False,
) -> Any:
    """
    Suspend a fact.
    """
    if undo:
        fact = crud.fact.undo_suspend(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    else:
        fact = crud.fact.suspend(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    return fact


@router.put("/report/{fact_id}", response_model=schemas.Fact)
def report_fact(
    *,
    perms: deps.CheckFactPerms = Depends(),
    undo: bool = False,
) -> Any:
    """
    Report a fact.
    """
    if undo:
        fact = crud.fact.undo_report(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    else:
        fact = crud.fact.report(db=perms.db, db_obj=perms.fact, user=perms.current_user)
    return fact
