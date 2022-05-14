import logging
from typing import List, Optional, Union

from app import models, schemas
from app.crud.base import CRUDBase
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDSTUDYSET(CRUDBase[models.StudySet, schemas.StudySetCreate, schemas.StudySetUpdate]):
    def create_with_facts(self, db: Session, *, obj_in: models.StudySet, facts: List[models.Fact]):
        db_obj = self.create(db, obj_in=obj_in)
        self.assign_facts(db, db_obj=db_obj, facts=facts)
        db.refresh(db_obj)
        return db_obj

    def assign_facts(self, *, db: Session, db_obj: models.StudySet, facts: List[models.Fact]) -> None:
        for fact in facts:
            self.assign_fact(db, db_obj=db_obj, fact=fact)

    def assign_fact(self, *, db: Session, db_obj: models.StudySet, fact: models.Fact) -> None:
        session_fact = models.Session_Fact(studyset_id=db_obj.id, fact_id=fact.fact_id)
        db.add(session_fact)
        db.commit()

    def get_study_set(self,
                      db: Session,
                      *,
                      user: models.User,
                      deck_ids: List[int] = None,
                      return_limit: Optional[int] = None,
                      send_limit: Optional[int] = 300,
                      ) -> Union[List[schemas.Fact], requests.exceptions.RequestException, json.decoder.JSONDecodeError]:


studyset = CRUDSTUDYSET(models.StudySet)
