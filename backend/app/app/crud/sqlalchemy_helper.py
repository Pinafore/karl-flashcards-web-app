from typing import List, Optional

from sqlalchemy import Column, func, not_
from sqlalchemy.orm import query
from app import crud, models, schemas
from app.core.config import settings


def filter_deck_ids(query: query, deck_ids: Optional[List[int]]):
    return query.filter(models.Fact.deck_id.in_(deck_ids)) if deck_ids else query


def filter_deck_id(query: query, deck_id: Optional[int]):
    return query.filter(models.Fact.deck_id == deck_id) if deck_id else query


def filter_ilike(query: query, model_attr: Column, filter_attr: Optional[str]):
    return query.filter(model_attr).ilike(filter_attr) if filter_attr else query


def filter_full_text_search(query: query, query_str: Optional[str]):
    return query.filter(
        models.Fact.__ts_vector__.op('@@')(func.plainto_tsquery('english', query_str))) if query_str else query


def filter_marked(query: query, marked: Optional[bool], user_id: int):
    if marked is not None:
        if marked:
            return query.filter(models.Fact.markers.any(id=user_id))
        else:
            return query.filter(not_(models.Fact.markers.any(id=user_id)))
    return query

# def is_test_deck(deck_id: int):
#     return deck_id == settings.TEST_DECK_ID
