from pydantic import BaseModel, Json


class Visualization(BaseModel):
    name: str
    schema: Json
