# from sqlalchemy.orm import Session
#
# from app import crud
# from app.schemas.fact import FactCreate, FactUpdate
# from app.tests.utils.user import create_random_user
# from app.tests.utils.utils import random_lower_string
#
#
# def test_create_fact(db: Session) -> None:
#     title = random_lower_string()
#     description = random_lower_string()
#     fact_in = FactCreate(title=title, description=description)
#     user = create_random_user(db)
#     fact = crud.fact.create_with_owner(db=db, obj_in=fact_in, owner_id=user.id)
#     assert fact.title == title
#     assert fact.description == description
#     assert fact.owner_id == user.id
#
#
# def test_get_fact(db: Session) -> None:
#     title = random_lower_string()
#     description = random_lower_string()
#     fact_in = FactCreate(title=title, description=description)
#     user = create_random_user(db)
#     fact = crud.fact.create_with_owner(db=db, obj_in=fact_in, owner_id=user.id)
#     stored_fact = crud.fact.get(db=db, id=fact.card_id)
#     assert stored_fact
#     assert fact.card_id == stored_fact.card_id
#     assert fact.title == stored_fact.title
#     assert fact.description == stored_fact.description
#     assert fact.owner_id == stored_fact.owner_id
#
#
# def test_update_fact(db: Session) -> None:
#     title = random_lower_string()
#     description = random_lower_string()
#     fact_in = FactCreate(title=title, description=description)
#     user = create_random_user(db)
#     fact = crud.fact.create_with_owner(db=db, obj_in=fact_in, owner_id=user.id)
#     description2 = random_lower_string()
#     fact_update = FactUpdate(description=description2)
#     fact2 = crud.fact.update(db=db, db_obj=fact, obj_in=fact_update)
#     assert fact.card_id == fact2.id
#     assert fact.title == fact2.title
#     assert fact2.description == description2
#     assert fact.owner_id == fact2.owner_id
#
#
# def test_delete_fact(db: Session) -> None:
#     title = random_lower_string()
#     description = random_lower_string()
#     fact_in = FactCreate(title=title, description=description)
#     user = create_random_user(db)
#     fact = crud.fact.create_with_owner(db=db, obj_in=fact_in, owner_id=user.id)
#     fact2 = crud.fact.remove(db=db, id=fact.card_id)
#     fact3 = crud.fact.get(db=db, id=fact.card_id)
#     assert fact3 is None
#     assert fact2.id == fact.card_id
#     assert fact2.title == title
#     assert fact2.description == description
#     assert fact2.owner_id == user.id
