from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app import crud, models, schemas


class CRUDFact(CRUDBase[models.Fact, schemas.FactCreate, schemas.FactUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: schemas.FactCreate, owner_id: int
    ) -> models.Fact:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, user: models.User, skip: int = None, limit: int = None
    ) -> List[models.Fact]:
        return (
            db.query(self.model)
                .filter(models.Fact.user_id == user.id)
                .offset(skip)
                .limit(limit)
                .all()
        )

    # def remove(self, db: Session, *, fact_id: int):
    #     new_suspend_create = SuspendedCreate(
    #         date_suspended=datetime.now(timezone('UTC')),
    #         fact_id=fact_id,
    #         delete=True,
    #     )
    #     new_suspend = Suspended(**new_suspend_create.dict())
    #     db_session.add(new_suspend)
    #     db_session.commit()
    #
    #     return db_session.query(models.Fact).filter(models.Fact.id == fact_id).first()


fact = CRUDFact(models.Fact)
