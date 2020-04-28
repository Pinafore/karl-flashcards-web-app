from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Fact])
def get_next_set(
    db: Session = Depends(deps.get_db),
    user_id: int = None,
    deck_ids: List[int] = None,
    limit: int = 20,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get next set of facts for review using user's schedule.
    Allows superusers to view anyone's future schedule.
    """
    if user_id:
        user = crud.user.get(db=db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not (crud.user.is_superuser(current_user) or user_id == current_user.id):
            raise HTTPException(status_code=400, detail="This user does not have the necessary permissions")
    else:
        user = current_user

    if deck_ids is None:
        facts = crud.fact.get_study_set(db=db, user=user, limit=limit)
    else:
        for deck_id in deck_ids:
            deck = crud.deck.get(db=db, id=deck_id)
            if not deck:
                raise HTTPException(status_code=404, detail="One or more of the specified decks does not exist")

        facts = crud.fact.get_study_set(db=db, user=user, deck_ids=deck_ids, limit=limit)
    return facts
