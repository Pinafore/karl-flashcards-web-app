from random import choice
from typing import List, Optional, Set, Union, Dict, Any, Tuple

from app.core.config import settings
from app.crud.base import CRUDBase
from app import crud, models
from app.models import User, Deck
from app.models.user_deck import User_Deck
from app.schemas import Permission, DeckType, Repetition, SetType
from app.schemas.deck import DeckCreate, DeckUpdate, SuperDeckCreate, SuperDeckUpdate
from sqlalchemy import func, not_, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true
from fastapi import HTTPException
from app.utils.utils import logger, log_time, time_it
from sqlalchemy.orm import joinedload


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
        if db_obj.deck_type == DeckType.hidden:
            user_deck = User_Deck(db_obj, user, Permission.viewer, repetition_model_override=self.select_repetition_given_counts(db, user=user))
        else:
            user_deck = User_Deck(db_obj, user, Permission.viewer)
        
        db.add(user_deck)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def select_repetition_given_counts(self, db: Session, *, user: User) -> Repetition:
        # Query the count of each repetition model for the user
        counts = (
            db.query(
                User_Deck.repetition_model_override,
                func.count(User_Deck.repetition_model_override).label('model_count')
            )
            .join(Deck, Deck.id == User_Deck.deck_id)
            .filter(Deck.deck_type == DeckType.hidden, User_Deck.owner_id == user.id)
            .group_by(User_Deck.repetition_model_override)
            .all()
        )

        # Convert counts to a dictionary
        model_counts = {model: count for model, count in counts if model in [Repetition.fsrs, Repetition.karl]}
        logger.info(str(model_counts))
        # If a model has not been used yet, set its count to 0
        for model in [Repetition.fsrs, Repetition.karl]:
            model_counts.setdefault(model, 0)

        # Find the model(s) with the minimum count
        min_count_models = [model for model, count in model_counts.items() if count == min(model_counts.values())]

        # Randomly select one of the least selected models
        selected_model = choice(min_count_models)

        return selected_model

    def get_multi_by_owner(
            self, db: Session, *, user: User, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[Deck]:
        decks = [deck for deck in user.decks] # Doesn't include test deck because that is hidden into all_decks
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

    def get_current_user_test_deck_id(self, db: Session, user: User) -> Optional[int]:
        deck, _ = self.get_current_user_test_deck(db=db, user=user)
        return deck.id if deck else None

    def get_current_user_test_deck(self, db: Session, user: User) -> Optional[Tuple[Deck, int]]:
        # Subquery to count the number of Session_Deck entries per User_Deck
        # Possibly, we can just check for the presence of a post test deck?
        subquery = (
            db.query(
                models.Session_Deck.deck_id,
                func.count().label('num_test_sets_completed')
            )
            .join(models.Session_Deck.studyset)
            .filter(models.StudySet.user_id == user.id)
            .group_by(models.Session_Deck.deck_id)
            .subquery()
        )

        # Main query to get the Deck along with the coalesced count of completed test sets
        test_deck = (
            db.query(
                models.Deck,
                func.coalesce(subquery.c.num_test_sets_completed, 0).label('num_test_sets_completed')
            )
            .join(models.User_Deck)  # Join User_Deck to filter by user and deck relationship
            .outerjoin(subquery, models.User_Deck.deck_id == subquery.c.deck_id)
            .filter(models.User_Deck.owner_id == user.id,
                    models.Deck.deck_type == DeckType.hidden,
                    or_(subquery.c.num_test_sets_completed == None,
                        subquery.c.num_test_sets_completed < settings.POST_TEST_TRIGGER + 1))
            .order_by(models.User_Deck.deck_id.asc())
            .first()
        )

        if test_deck == None:
            return None, settings.POST_TEST_TRIGGER + 1

        # Directly return the result of the query
        return test_deck

    def get_all_test_decks(self, db: Session) -> List[Deck]:
        return db.query(self.model).filter(self.model.deck_type == DeckType.hidden).order_by(self.model.id.asc()).all()

    def get_all_test_deck_ids(self, db: Session) -> Set[int]:
        test_decks = self.get_all_test_decks(db)
        return {deck.id for deck in test_decks}

    def assign_test_decks(self, db: Session, user: User) -> List[Deck]:
        test_decks = self.get_all_test_decks(db)
        if not test_decks:
            raise HTTPException(561, detail="No Test Deck Found")
        
        for deck in test_decks:
            if deck not in user.all_decks:
                self.assign_viewer(db=db, db_obj=deck, user=user)
                
        return test_decks

    def assign_test_decks_to_all(self, db: Session):
        all_users = db.query(models.User).all()
        for found_user in all_users:
            self.assign_test_decks(db=db,user=found_user)
    
    def check_for_test_deck_ids(self, db, deck_ids):
        if not deck_ids:
            return []
        test_deck_ids = self.get_all_test_deck_ids(db=db)
        if set(deck_ids).intersection(test_deck_ids):
            raise HTTPException(status_code=557, detail="This deck is currently unavailable")
        
    def get_user_decks_given_ids(self, db: Session, user: models.User, deck_ids: List[int] = None) -> List[models.Deck]:
        decks = []
        if deck_ids is None:
            return decks 
        for deck_id in deck_ids:
            deck = self.get(db=db, id=deck_id)
            if not deck:
                raise HTTPException(status_code=404, detail="One or more of the specified decks does not exist")
            if user not in deck.users:
                raise HTTPException(status_code=450,
                                        detail="This user does not have the necessary permission to access one or more"
                                            " of the specified decks")
            decks.append(deck)
        return decks

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
            self, db: Session, *, db_obj: Deck, obj_in: Union[DeckUpdate, SuperDeckUpdate, Dict[str, Any]]
    ) -> Deck:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def mark_user_deck_completed(self, db: Session, db_obj: Deck, user: User):
        user_deck_association = db.query(User_Deck).filter_by(deck_id=db_obj.id, owner_id=user.id).first()
        
        if not user_deck_association:
            raise HTTPException(status_code=576, detail=f"Attempted to mark non-existent user deck completed. User id: {user.id}. Deck id: {db_obj.id}")
        user_deck_association.completed = True
        db.commit()
        return

    def remove_for_user(self, db: Session, *, db_obj: Deck, user: User) -> Deck:
        # Check if the user is associated with the deck using a direct query
        user_deck_association = db.query(User_Deck).filter_by(deck_id=db_obj.id, owner_id=user.id).first()
        
        if user_deck_association:
            db.delete(user_deck_association)
            
            existing_studyset = crud.studyset.find_active_study_set(db, user)
            if isinstance(existing_studyset, models.StudySet) and existing_studyset.set_type == SetType.normal:
                crud.studyset.mark_retired(db, db_obj=existing_studyset)
            
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def soft_delete_deck(self, db: Session, db_obj: Deck) -> Deck:
        
        if not db_obj:
            raise HTTPException(status_code=404, detail="Deck not found")
        
        db_obj.deck_type = DeckType.deleted
        
        db.query(User_Deck).filter_by(deck_id=db_obj.id).delete()
        
        associated_studysets = db.query(models.StudySet).join(models.Session_Deck).filter(models.Session_Deck.deck_id == db_obj.id).all()
        for studyset in associated_studysets:
            crud.studyset.mark_retired(db, db_obj=studyset)
        
        db.commit()
        db.refresh(db_obj)
    
        return db_obj



deck = CRUDDeck(Deck)
