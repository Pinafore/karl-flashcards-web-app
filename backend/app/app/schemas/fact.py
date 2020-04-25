from typing import Optional

from pydantic import BaseModel


# Shared properties
class FactBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


# Properties to receive on fact creation
class FactCreate(FactBase):
    title: str


# Properties to receive on fact update
class FactUpdate(FactBase):
    pass


# Properties shared by models stored in DB
class FactInDBBase(FactBase):
    id: int
    title: str
    owner_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Fact(FactInDBBase):
    pass


# Properties properties stored in DB
class FactInDB(FactInDBBase):
    pass
