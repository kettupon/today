from pydantic import BaseModel

class Item(BaseModel):
    name: str

    class Config:
        orm_mode = True
