from pydantic import BaseModel, Json


class Visualization(BaseModel):
    name: str
    spec: Json
