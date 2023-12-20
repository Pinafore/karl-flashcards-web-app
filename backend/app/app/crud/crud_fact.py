import json
from datetime import datetime
from tempfile import SpooledTemporaryFile
from typing import List, Union, Dict, Any, Optional

import pandas
from fastapi.encoders import jsonable_encoder
from pytz import timezone
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, Query

from app import crud, models, schemas
from app.crud.base import CRUDBase
from app.schemas import Log, DeckType
from app.utils.utils import logger, log_time, time_it


class CRUDFact(CRUDBase[models.Fact, schemas.FactCreate, schemas.FactUpdate]):
    def get(self, db: Session, id: Any) -> Optional[models.Fact]:
        db_obj = db.query(self.model).filter(models.Fact.fact_id == id).first()
        return db_obj

    # noinspection PyCallingNonCallable
    def get_schema_with_perm(self, db_obj: models.Fact, user: models.User) -> schemas.Fact:
        schema = schemas.Fact.from_orm(db_obj)
        schema.permission = db_obj.permissions(user)
        schema.marked = db_obj.is_marked(user)
        schema.suspended = db_obj.is_suspended(user)
        schema.reports = db_obj.find_reports(user)
        return schema

    def create_with_owner(
            self, db: Session, *, obj_in: schemas.FactCreate, user: models.User
    ) -> models.Fact:
        obj_in_data = jsonable_encoder(obj_in)
        now = datetime.now(timezone('UTC')).isoformat()
        db_obj = models.Fact(**obj_in_data,
                             user_id=user.id,
                             create_date=now,
                             update_date=now)
        db.add(db_obj)
        db.commit()
        return db_obj

    def get_multi_by_owner(
            self,
            db: Session,
            *,
            user: Optional[models.User] = None,
            skip: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> List[models.Fact]:
        query = db.query(self.model)
        if user:
            query = query.filter(models.Fact.user_id == user.id)
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.offset(limit)
        return query.all()

    def update(
            self, db: Session, *, db_obj: models.Fact, obj_in: Union[schemas.FactUpdate, Dict[str, Any]]
    ) -> models.Fact:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        update_data["update_date"] = datetime.now(timezone('UTC')).isoformat()
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def remove(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        now = datetime.now(timezone('UTC'))
        delete = models.Deleted(deleter=user, deleted_fact=db_obj, date_deleted=now)
        db.add(delete)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=now,
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.delete,
            details={"study_system": user.repetition_model, "recall_target": user.recall_target}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def suspend(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        now = datetime.now(timezone('UTC'))
        suspend = models.Suspended(suspender=user,
                                   suspended_fact=db_obj,
                                   date_suspended=now)
        db.add(suspend)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=now,
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.suspend,
            details={"study_system": user.repetition_model, "recall_target": user.recall_target}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def report(
            self, db: Session, *, db_obj: models.Fact, user: models.User, suggestion: schemas.FactToReport
    ) -> models.Fact:
        now = datetime.now(timezone('UTC'))
        report = models.Reported(reporter=user,
                                 reported_fact=db_obj,
                                 date_reported=datetime.now(timezone('UTC')),
                                 suggestion=suggestion)
        db.add(report)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=now,
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.report,
            details={"study_system": user.repetition_model, "recall_target": user.recall_target}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def mark(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        now = datetime.now(timezone('UTC'))

        mark = models.Marked(marker=user, marked_fact=db_obj, date_marked=now)
        db.add(mark)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=now,
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.mark,
            details={"study_system": user.repetition_model, "recall_target": user.recall_target}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    # noinspection PyTypeChecker
    def undo_remove(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Deleted).filter(
            and_(models.Deleted.fact_id == db_obj.fact_id, models.Deleted.user_id == user.id)).delete(
            synchronize_session=False)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.undo_delete,
            details={"study_system": user.repetition_model, "recall_target": user.recall_target}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def undo_suspend(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Suspended) \
            .filter(and_(models.Suspended.suspended_fact == db_obj,
                         models.Suspended.suspender == user)).delete(synchronize_session=False)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.undo_suspend,
            details={"study_system": user.repetition_model, "recall_target": user.recall_target}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def undo_report(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:

        db.query(models.Reported) \
            .filter(and_(models.Reported.fact_id == db_obj.fact_id,
                         models.Reported.user_id == user.id)).delete(synchronize_session=False)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.undo_report,
            details={"study_system": user.repetition_model, "recall_target": user.recall_target}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def resolve_report(
            self, db: Session, *, user: models.User, db_obj: models.Fact
    ) -> models.Fact:
        db.query(models.Reported) \
            .filter(models.Reported.fact_id == db_obj.fact_id).delete(
            synchronize_session=False)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.resolve_report,
            details={"study_system": user.repetition_model, "recall_target": user.recall_target}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def undo_mark(
            self, db: Session, *, db_obj: models.Fact, user: models.User
    ) -> models.Fact:
        db.query(models.Marked) \
            .filter(and_(models.Marked.marked_fact == db_obj,
                         models.Marked.marker == user)).delete(synchronize_session=False)
        db.commit()

        history_in = schemas.HistoryCreate(
            time=datetime.now(timezone('UTC')).isoformat(),
            user_id=user.id,
            fact_id=db_obj.fact_id,
            log_type=schemas.Log.undo_mark,
            details={"study_system": user.repetition_model, "recall_target": user.recall_target}
        )
        crud.history.create(db=db, obj_in=history_in)
        return db_obj

    def build_facts_query(self, db: Session, *, user: models.User,
                          filters: schemas.FactSearch = schemas.FactSearch()) -> Query:
        if filters.show_hidden:
            visible_decks = (
                db.query(models.Deck.id).filter(models.Deck.deck_type == DeckType.hidden).join(models.User_Deck).filter(
                    models.User_Deck.owner_id == user.id).subquery())
        else:
            visible_decks = (
                db.query(models.Deck.id).filter(models.Deck.deck_type.in_([DeckType.default, DeckType.public])).join(models.User_Deck).filter(
                    models.User_Deck.owner_id == user.id).subquery())
        user_facts = (db.query(models.Fact).join(visible_decks, models.Fact.deck_id == visible_decks.c.id).filter(
            models.Fact.user_id == user.id))

        deck_owners = (db.query(models.User_Deck.deck_id, models.User_Deck.owner_id)
                       .outerjoin(visible_decks)
                       .filter(models.User_Deck.permissions == schemas.Permission.owner).subquery())
        filtered_facts = (db.query(models.Fact)
                          .join(visible_decks, models.Fact.deck_id == visible_decks.c.id)
                          .join(deck_owners,
                                and_(models.Fact.deck_id == deck_owners.c.deck_id,
                                     models.Fact.user_id == deck_owners.c.owner_id)))
        facts_query = (user_facts.union(filtered_facts))
        if filters.studyable:
            facts_query = (facts_query
                           .outerjoin(models.Deleted,
                                      and_(models.Fact.fact_id == models.Deleted.fact_id,
                                           models.Deleted.user_id == user.id))
                           .filter(models.Deleted.user_id == None)  # keeps only facts join did not indicate deletion
                           .outerjoin(models.Reported,
                                      and_(models.Fact.fact_id == models.Reported.fact_id,
                                           models.Reported.user_id == user.id)
                                      )
                           .filter(models.Reported.user_id == None)
                           .outerjoin(models.Suspended,
                                      and_(models.Fact.fact_id == models.Suspended.fact_id,
                                           models.Suspended.user_id == user.id)
                                      )
                           .filter(models.Suspended.user_id == None))
        else:
            facts_query = (facts_query
                           .outerjoin(models.Deleted,
                                      and_(models.Fact.fact_id == models.Deleted.fact_id,
                                           models.Deleted.user_id == user.id))
                           .filter(models.Deleted.user_id == None))
            if filters.suspended is not None:
                if filters.suspended:
                    facts_query = facts_query.join(models.Suspended).filter(models.Suspended.user_id == user.id)
                else:
                    facts_query = (facts_query
                                   .outerjoin(models.Suspended,
                                              and_(models.Fact.fact_id == models.Suspended.fact_id,
                                                   models.Suspended.user_id == user.id)
                                              )
                                   .filter(models.Suspended.user_id == None))

            if filters.reported is not None:
                if filters.reported:
                    facts_query = facts_query.join(models.Reported)
                    if not user.is_superuser:
                        facts_query = facts_query.filter(models.Reported.user_id == user.id)
                else:
                    facts_query = (facts_query
                                   .outerjoin(models.Reported,
                                              and_(models.Fact.fact_id == models.Reported.fact_id,
                                                   models.Reported.user_id == user.id)
                                              )
                                   .filter(models.Reported.user_id == None))
        facts_query = crud.helper.filter_full_text_search(query=facts_query, query_str=filters.all)
        facts_query = crud.helper.filter_ilike(query=facts_query, model_attr=models.Fact.text,
                                                          filter_attr=filters.text)
        facts_query = crud.helper.filter_ilike(query=facts_query, model_attr=models.Fact.answer,
                                                          filter_attr=filters.answer)
        facts_query = crud.helper.filter_ilike(query=facts_query, model_attr=models.Fact.category,
                                                          filter_attr=filters.category)
        facts_query = crud.helper.filter_ilike(query=facts_query, model_attr=models.Fact.identifier,
                                                          filter_attr=filters.identifier)
        facts_query = crud.helper.filter_deck_ids(query=facts_query, deck_ids=filters.deck_ids)
        facts_query = crud.helper.filter_deck_id(query=facts_query, deck_id=filters.deck_id)
        facts_query = crud.helper.filter_marked(query=facts_query, marked=filters.marked, user_id=user.id)
        
        return facts_query

    @time_it
    def count_eligible_facts(
            self, query: Query
    ) -> int:
        return query.distinct().count()

    @time_it
    def get_eligible_facts(
            self, query: Query, skip: int = None, limit: int = None, randomize: bool = False
    ) -> List[models.Fact]:
        if randomize:
            query = query.order_by(func.random())
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        facts = query.all()
        return facts

    

    def load_json_facts(self, db: Session, file: SpooledTemporaryFile, user: models.User) -> None:
        count = 0
        json_data = json.load(file)
        for fact_obj in json_data:
            self.create_fact(db, fact_obj, user, DeckType.default)
            count += 1
        logger.info(f"{count} facts loaded from txt file")

    def load_txt_facts(self, db: Session, file: SpooledTemporaryFile, user: models.User,
                       props: schemas.FileProps) -> None:
        count = 0
        with file as f:
            df = pandas.read_csv(f, sep=props.delimeter, names=props.headers, index_col=False)
            for index, fact_obj in df.iterrows():
                if schemas.Field.deck in props.headers and not pandas.isna(fact_obj[schemas.Field.deck]):
                    deck_id = crud.deck.find_or_create(db, proposed_deck=fact_obj["deck"], user=user).id
                else:
                    deck_id = props.default_deck.id
                fact_in = schemas.FactCreate(
                    text=fact_obj[schemas.Field.text],
                    answer=fact_obj[schemas.Field.answer],
                    deck_id=deck_id,
                    answer_lines=[fact_obj[schemas.Field.answer]],
                    extra={"type": "uploaded"}
                )
                if schemas.Field.identifier in props.headers and not pandas.isna(fact_obj[schemas.Field.identifier]):
                    fact_in.identifier = fact_obj[schemas.Field.identifier]
                if schemas.Field.category in props.headers and not pandas.isna(fact_obj[schemas.Field.category]):
                    fact_in.identifier = fact_obj[schemas.Field.category]
                crud.fact.create_with_owner(db, obj_in=fact_in, user=user)
                count += 1
        logger.info(f"{count} facts loaded from txt file")

    def create_fact(self, db: Session, fact_obj: Any, user: models.User, deck_type: DeckType) -> None:
        deck = crud.deck.find_or_create(db, proposed_deck=fact_obj["deck"], user=user, deck_type=deck_type)
        fact_in = schemas.FactCreate(
            text=fact_obj["text"],
            answer=fact_obj["answer"],
            deck_id=deck.id,
            answer_lines=fact_obj["answer_lines"],
            identifier=fact_obj["identifier"],
            category=fact_obj["category"],
            extra=fact_obj["extra"]
        )
        crud.fact.create_with_owner(db, obj_in=fact_in, user=user)


fact = CRUDFact(models.Fact)
