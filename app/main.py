from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from .database import engine, SessionLocal, database
from .models import Base, Item as DBItem
from .schemas import Item

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    items = db.query(DBItem).all()
    return templates.TemplateResponse("index.html", {"request": request, "items": items})

@app.post("/add/")
async def add_item(name: str = Form(...), db: Session = Depends(get_db)):
    db_item = DBItem(name=name)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": "Item added"}

@app.post("/delete/")
async def delete_item(name: str = Form(...), db: Session = Depends(get_db)):
    db.query(DBItem).filter(DBItem.name == name).delete()
    db.commit()
    return {"message": "Item deleted"}
