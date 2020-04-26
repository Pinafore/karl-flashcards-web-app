from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true

from app.crud.base import CRUDBase
from app.models import User, Deck
from app.schemas.deck import DeckCreate, DeckUpdate


class CRUDDeck(CRUDBase[Deck, DeckCreate, DeckUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: DeckCreate, user: User
    ) -> Deck:
        db_obj = self.create(db, obj_in=obj_in)
        db_obj = self.assign(db, db_obj=db_obj, user=user)
        return db_obj

    def assign(
        self, db: Session, *, db_obj: Deck, user: User
    ) -> Deck:
        db_obj.users.append(user)
        db.add(db_obj)
        db.commit()
        return db_obj

    def get_multi_by_owner(
        self, *, user: User, skip: int = None, limit: int = None
    ) -> List[Deck]:
        if skip and limit:
            return user.decks[skip:skip+limit]
        elif skip:
            return user.decks[skip:]
        elif limit:
            return user.decks[:limit]
        else:
            return user.decks

    def get_public(
            self, db: Session
    ) -> List[Deck]:
        return (db.query(self.model)
                .filter(Deck.public == true())
                .offset(1)  # don't show Default
                .all()
                )

    def find_or_create(
            self, db: Session, *, proposed_deck: str, user: User
    ) -> Deck:
        user_decks = self.get_multi_by_owner(user=user)
        owned_deck = [user_deck for user_deck in user_decks if user_deck.title == proposed_deck]
        if owned_deck:
            user_deck = owned_deck[0]
        else:
            user_deck = self.create_with_owner(db=db, obj_in=DeckCreate(title=proposed_deck), user=user)
        return user_deck

    def remove_for_user(
            self, db: Session, *, db_obj: Deck, user: User
    ) -> Deck:
        if user in db_obj.users:
            db_obj.users.remove(user)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj


deck = CRUDDeck(Deck)
