from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app import models, schemas


def public_facts_subquery(db: Session):
    return (db
            .query(models.Fact)
            .join(models.Fact.deck)
            .filter(models.Deck.user_decks.any(permissions=schemas.Permission.owner)).subquery())


def directly_owned_facts_subquery(db: Session, user: models.User):
    return db.query(models.Fact).filter(models.Fact.user_id == user.id).subquery()


def facts_from_owned_decks_subquery(db: Session, user: models.User):
    return db.query(models.Fact).join(models.Fact.deck).filter(models.Deck.user_decks.any(owner_id=user.id)).subquery()


def user_viewable_facts(db: Session, user: models.User):
    public_facts = public_facts_subquery(db)
    facts_from_owned_decks = facts_from_owned_decks_subquery(db, user=user)
    directly_owned_facts = directly_owned_facts_subquery(db, user=user)
    return (db
            .query(models.Fact)
            .filter(or_(and_(models.Fact.in_(public_facts),
                             models.Fact.in_(facts_from_owned_decks)),
                         models.Fact.in_(directly_owned_facts))))
