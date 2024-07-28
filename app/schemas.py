from pydantic import BaseModel

class Item(BaseModel):
    name: str

    class Config:
        from_attributes = True  # Use 'from_attributes' instead of 'orm_mode'
