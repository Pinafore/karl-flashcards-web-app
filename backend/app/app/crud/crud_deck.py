import logging
from typing import List, Optional, Union, Dict, Any

from app.core.config import settings
from app.crud.base import CRUDBase
from app.models import User, Deck
from app.models.user_deck import User_Deck
from app.schemas import Permission
from app.schemas.deck import DeckCreate, DeckUpdate, SuperDeckCreate, SuperDeckUpdate
from sqlalchemy import not_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDDeck(CRUDBase[Deck, DeckCreate, DeckUpdate]):
    def create_with_owner(
            self, db: Session, *, obj_in: Union[DeckCreate, SuperDeckCreate], user: User
    ) -> Deck:
        db_obj = self.create(db, obj_in=obj_in)
        db_obj = self.assign_owner(db, db_obj=db_obj, user=user)
        return db_obj

    def assign_owner(
            self, db: Session, *, db_obj: Deck, user: User
    ) -> Deck:
        user_deck = User_Deck(db_obj, user, Permission.owner)

        # db_obj.user_decks.append(User_Deck(db_obj, user, Permission.viewer))
        db.add(user_deck)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def assign_viewer(
            self, db: Session, *, db_obj: Deck, user: User
    ) -> Deck:
        # db_obj.user_decks.append(User_Deck(db_obj, user, Permission.viewer))
        user_deck = User_Deck(db_obj, user, Permission.viewer)
        db.add(user_deck)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
            self, *, user: User, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[Deck]:
        if skip and limit:
            return user.decks[skip:skip + limit]
        elif skip:
            return user.decks[skip:]
        elif limit:
            return user.decks[:limit]
        else:
            return user.decks

    def get_public(
            self, db: Session, unowned: bool, user: User
    ) -> List[Deck]:
        query = db.query(self.model).filter(Deck.public == true(), Deck.id != 1,
                                            Deck.id != 2)  # Don't return "default" or Jeopardy
        if unowned:
            query = query.filter(not_(Deck.users.any(id=user.id)))
        return query.all()

    def get_test_deck_id(self, db: Session, user: User) -> int:
        return self.get_create_test_deck(db, user).id

    def get_create_test_deck(self, db: Session, user: User) -> Deck:
        return self.find_or_create(db, proposed_deck=settings.TEST_DECK_NAME, user=user, public=True)

    def find_or_create(
            self, db: Session, *, proposed_deck: str, user: User, public: bool = False
    ) -> Deck:
        user_decks = self.get_multi_by_owner(user=user)
        owned_deck = [user_deck for user_deck in user_decks if user_deck.title == proposed_deck]
        if owned_deck:
            user_deck = owned_deck[0]
        else:
            user_deck = self.create_with_owner(db=db, obj_in=SuperDeckCreate(title=proposed_deck, public=public),
                                               user=user)
        return user_deck

    def update(
            self, db: Session, *, db_obj: User, obj_in: Union[DeckUpdate, SuperDeckUpdate, Dict[str, Any]]
    ) -> Deck:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def remove_for_user(
            self, db: Session, *, db_obj: Deck, user: User
    ) -> Deck:
        if user in db_obj.users:
            db_obj.users.remove(user)
            # db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj


deck = CRUDDeck(Deck)
