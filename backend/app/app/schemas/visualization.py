from pydantic import BaseModel, Json


class Visualization(BaseModel):
    name: str
    specs: str
