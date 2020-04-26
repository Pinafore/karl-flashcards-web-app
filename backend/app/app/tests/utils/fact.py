# from typing import Optional
#
# from sqlalchemy.orm import Session
#
# from app import crud, models
# from app.schemas.fact import FactCreate
# from app.tests.utils.user import create_random_user
# from app.tests.utils.utils import random_lower_string
#
#
# def create_random_fact(db: Session, *, owner_id: Optional[int] = None) -> models.Fact:
#     if owner_id is None:
#         user = create_random_user(db)
#         owner_id = user.id
#     title = random_lower_string()
#     description = random_lower_string()
#     fact_in = FactCreate(title=title, description=description, id=id)
#     return crud.fact.create_with_owner(db=db, obj_in=fact_in, owner_id=owner_id)
