from .crud_deck import deck
from .crud_fact import fact
from .crud_history import history
from .crud_user import user

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.fact import Fact
# from app.schemas.fact import FactCreate, FactUpdate

# fact = CRUDBase[Fact, FactCreate, FactUpdate](Fact)
