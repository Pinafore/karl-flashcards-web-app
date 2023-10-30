import math
from typing import List, Optional
from fastapi import HTTPException

from sqlalchemy import Column, and_, func, not_
from sqlalchemy.orm import query
from app import crud, models, schemas
from app.core.config import settings
from app.utils.utils import logger, log_time, time_it

class SQLAlchemyHelpers():
    def filter_deck_ids(self, query: query, deck_ids: Optional[List[int]]):
        return query.filter(models.Fact.deck_id.in_(deck_ids)) if deck_ids else query


    def filter_deck_id(self, query: query, deck_id: Optional[int]):
        return query.filter(models.Fact.deck_id == deck_id) if deck_id else query


    def filter_ilike(self, query: query, model_attr: Column, filter_attr: Optional[str]):
        return query.filter(model_attr.ilike(f'%{filter_attr}%')) if filter_attr else query


    def filter_full_text_search(self, query: query, query_str: Optional[str]):
        return query.filter(
            models.Fact.__ts_vector__.op('@@')(func.plainto_tsquery('english', query_str))) if query_str else query


    def filter_marked(self, query: query, marked: Optional[bool], user_id: int):
        if marked is not None:
            if marked:
                return query.filter(models.Fact.markers.any(id=user_id))
            else:
                return query.filter(not_(models.Fact.markers.any(id=user_id)))
        return query

    def filter_only_new_facts(self, query: query, user_id: int, log_type: schemas.Log):
        return query.outerjoin(
                models.History, and_(
                    models.Fact.fact_id == models.History.fact_id,
                    models.History.user_id == user_id,
                    models.History.log_type == log_type
                )).filter(
                models.History.id == None)

    def filter_only_incorrectly_reviewed_facts(self, query: query, user_id: int, log_type: schemas.Log):
        return query.join(
                models.History, and_(
                    models.Fact.fact_id == models.History.fact_id,
                    models.History.user_id == user_id,
                    models.History.log_type == log_type,
                    models.History.correct == False))

    def filter_only_reviewed_facts(self, query: query, user_id: int, log_type: schemas.Log):
        return query.join(
                models.History, and_(
                    models.Fact.fact_id == models.History.fact_id,
                    models.History.user_id == user_id,
                    models.History.log_type == log_type))
    # def is_test_deck(deck_id: int):
    #     return deck_id == settings.TEST_DECK_ID

    def combine_two_fact_sets(self, random_facts: List[models.Fact], old_facts: List[models.Fact], return_limit: int):
        len_random_facts = len(random_facts)
        len_old_facts = len(old_facts)
        lower_lim, upper_lim = math.floor(return_limit / 2), math.ceil(return_limit / 2)
        if len_random_facts >= upper_lim and len_old_facts >= upper_lim:
            facts = random_facts[:lower_lim] + old_facts[:upper_lim]
        elif len_random_facts < upper_lim:
            facts = random_facts + old_facts[:return_limit - len_random_facts]
        elif len_old_facts < upper_lim:
            facts = random_facts[:return_limit - len_old_facts] + old_facts 
        return facts

helper = SQLAlchemyHelpers()