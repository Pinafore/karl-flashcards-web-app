from datetime import datetime
from typing import Any, List, Union

from app import crud, models, schemas
from app.api import deps
from fastapi import APIRouter, Depends, HTTPException, Query
from pytz import timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.schemas import DeckType

router = APIRouter()


@router.get("/", response_model=List[schemas.Deck])
def read_decks(
        db: Session = Depends(deps.get_db),
        paginate: deps.Paginate = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve decks.
    """
    if crud.user.is_superuser(current_user):
        decks = crud.deck.get_multi(db, skip=paginate.skip, limit=paginate.limit)
    else:
        decks = crud.deck.get_multi_by_owner(
            db, user=current_user, skip=paginate.skip, limit=paginate.limit
        )
    return decks


@router.get("/public", response_model=List[schemas.Deck])
def read_open_decks(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),  # noqa
        unowned: bool = True,
) -> Any:
    """
    Retrieve decks.
    """
    decks = crud.deck.get_public(db, unowned=unowned, user=current_user)

    return decks


@router.post("/", response_model=schemas.Deck)
def create_deck(
        *,
        db: Session = Depends(deps.get_db),
        deck_in: Union[schemas.DeckCreate, schemas.SuperDeckCreate],
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new deck.
    """
    deck = crud.deck.create_with_owner(db=db, obj_in=deck_in, user=current_user)
    return deck


@router.put("/", response_model=List[schemas.Deck])
def assign_decks(
        *,
        db: Session = Depends(deps.get_db),
        deck_ids: List[int] = Query(...),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
        Assign an existing deck to a new user.
    """

    decks = []
    for deck_id in deck_ids:
        deck = crud.deck.get(db=db, id=deck_id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")

        if deck.deck_type == DeckType.public:
            if deck not in current_user.decks:
                deck = crud.deck.assign_viewer(db=db, db_obj=deck, user=current_user)
                decks.append(deck)
        else:
            raise HTTPException(status_code=401, detail="User does not have permission to add one of the specified "
                                                        "decks")

    history_in = schemas.HistoryCreate(
        time=datetime.now(timezone('UTC')).isoformat(),
        user_id=current_user.id,
        log_type=schemas.Log.assign_viewer,
        details={"study_system": current_user.repetition_model, "decks": deck_ids}
    )
    crud.history.create(db=db, obj_in=history_in)
    return decks


@router.put("/{deck_id}", response_model=schemas.Deck)
def update_deck(
        *,
        db: Session = Depends(deps.get_db),
        deck_id: int,
        deck_in: Union[schemas.DeckUpdate, schemas.SuperDeckUpdate],
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an deck.
    """
    deck = crud.deck.get(db=db, id=deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if not crud.user.is_superuser(current_user) and deck.deck_type != DeckType.default:
        raise HTTPException(status_code=401, detail="Not enough permissions")
    deck = crud.deck.update(db=db, db_obj=deck, obj_in=deck_in)
    return deck


@router.get("/{deck_id}", response_model=schemas.Deck)
def read_deck(
        *,
        db: Session = Depends(deps.get_db),
        deck_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get deck by ID.
    """
    deck = crud.deck.get(db=db, id=deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if crud.user.is_superuser(current_user) or deck in current_user.decks or deck.deck_type != DeckType.default:
        return deck
    else:
        raise HTTPException(status_code=401, detail="Not enough permissions")


@router.delete("/{deck_id}", response_model=schemas.Deck)
def delete_deck(
        *,
        db: Session = Depends(deps.get_db),
        deck_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a deck for a user.
    """
    deck = crud.deck.get(db=db, id=deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    deck = crud.deck.remove_for_user(db=db, db_obj=deck, user=current_user)
    return deck

@router.delete("/bulk/{deck_id}", response_model=schemas.Deck)
def delete_deck_for_all(
        *,
        db: Session = Depends(deps.get_db),
        deck_id: int,
        current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a deck for all users.
    """
    deck = crud.deck.get(db=db, id=deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    deck = crud.deck.soft_delete_deck(db=db, db_obj=deck)
    return deck
