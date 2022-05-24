import logging
from typing import List, Optional, Union, Dict, Any

from app.core.config import settings
from app.crud.base import CRUDBase
from app import crud, models
from app.models import User, Deck
from app.models.user_deck import User_Deck
from app.schemas import Permission, DeckType
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
            self, db: Session, *, user: User, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[Deck]:
        decks = [deck for deck in user.decks if deck.id != self.get_test_deck_id(db=db)]
        if skip and limit:
            decks = decks[skip:skip + limit]
        elif skip:
            decks = decks[skip:]  # Should check that skip is possible
        elif limit:
            decks = decks[:limit]
        return decks

    def get_public(
            self, db: Session, unowned: bool, user: User
    ) -> List[Deck]:
        query = db.query(self.model).filter(Deck.deck_type == DeckType.public,
                                            Deck.id != 1)
        if unowned:
            query = query.filter(not_(Deck.users.any(id=user.id)))
        return query.all()

    def get_test_deck_id(self, db: Session) -> Optional[int]:
        deck = self.get_test_deck(db=db)
        return deck.id if deck else None

    def get_test_deck(self, db: Session) -> Optional[Deck]:
        return db.query(self.model).filter(Deck.deck_type == DeckType.hidden).first()

    def assign_test_deck(self, db: Session, user: User) -> Deck:
        deck = self.get_test_deck(db)
        if deck:
            if deck not in user.decks:
                self.assign_viewer(db=db, db_obj=deck, user=user)
        else:
            self.create_with_owner(db=db,
                                   obj_in=SuperDeckCreate(title=settings.TEST_DECK_NAME, deck_type=DeckType.hidden),
                                   user=user)
        return deck

    def find_or_create(
            self, db: Session, *, proposed_deck: str, user: User, deck_type: DeckType = DeckType.default
    ) -> Deck:
        user_decks = self.get_multi_by_owner(db, user=user)
        owned_deck = [user_deck for user_deck in user_decks if user_deck.title == proposed_deck]
        if owned_deck:
            user_deck = owned_deck[0]
        else:
            user_deck = self.create_with_owner(db=db, obj_in=SuperDeckCreate(title=proposed_deck, deck_type=deck_type),
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
            existing_studyset = crud.studyset.find_existing_study_set(db, user)
            if isinstance(existing_studyset, models.StudySet):
                crud.studyset.mark_retired(db, db_obj=existing_studyset)
            db.commit()
            db.refresh(db_obj)
        return db_obj


deck = CRUDDeck(Deck)
