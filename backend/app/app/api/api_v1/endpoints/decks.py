from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Deck])
def read_decks(
    db: Session = Depends(deps.get_db),
    common: deps.SkipLimit = Depends(),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve decks.
    """
    if crud.user.is_superuser(current_user):
        decks = crud.deck.get_multi(db, skip=common.skip, limit=common.limit)
    else:
        decks = crud.deck.get_multi_by_owner(
            user=current_user, skip=common.skip, limit=common.limit
        )
    return decks


@router.get("/public", response_model=List[schemas.Deck])
def read_open_decks(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),  # noqa
):
    """
    Retrieve decks.
    """
    decks = crud.deck.get_public(db)

    return decks


@router.post("/", response_model=schemas.Deck)
def create_deck(
    *,
    db: Session = Depends(deps.get_db),
    deck_in: schemas.DeckCreate,
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

    print("CALLING ASSIGNED DECKS")
    decks = []
    for deck_id in deck_ids:
        deck = crud.deck.get(db=db, id=deck_id)
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")

        if deck.public or crud.user.is_superuser(current_user):
            if deck not in current_user.decks:
                deck = crud.deck.assign(db=db, db_obj=deck, user=current_user)
                decks.append(deck)
        else:
            raise HTTPException(status_code=404, detail="User does not have permission to add one of the specified "
                                                        "decks")
    return decks


@router.put("/{deck_id}", response_model=schemas.Deck)
def update_deck(
    *,
    db: Session = Depends(deps.get_db),
    deck_id: int,
    deck_in: schemas.DeckUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an deck.
    """
    print("DO YOU SEE ME")
    deck = crud.deck.get(db=db, id=deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if not crud.user.is_superuser(current_user) and deck.public:
        raise HTTPException(status_code=400, detail="Not enough permissions")
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
    if crud.user.is_superuser(current_user) or deck in current_user.decks or deck.public:
        return deck
    else:
        raise HTTPException(status_code=400, detail="Not enough permissions")


@router.delete("/{deck_id}", response_model=schemas.Deck)
def delete_deck(
    *,
    db: Session = Depends(deps.get_db),
    deck_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an deck.
    """
    deck = crud.deck.get(db=db, id=deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    deck = crud.deck.remove_for_user(db=db, db_obj=deck, user=current_user)
    return deck
