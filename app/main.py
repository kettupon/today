from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, database
from .models import Base, Item as DBItem
from .schemas import Item

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)

clients = []

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Dependency to get the SQLAlchemy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    items = db.query(DBItem).all()
    return templates.TemplateResponse("index.html", {"request": request, "items": items})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

@app.post("/add/")
async def add_item(name: str = Form(...), db: Session = Depends(get_db)):
    db_item = DBItem(name=name)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    # Notify all connected clients
    for client in clients:
        await client.send_text(f"Item added: {db_item.name}")
    return {"message": "Item added"}

@app.post("/delete/")
async def delete_item(name: str = Form(...), db: Session = Depends(get_db)):
    db.query(DBItem).filter(DBItem.name == name).delete()
    db.commit()
    # Notify all connected clients
    for client in clients:
        await client.send_text(f"Item deleted: {name}")
    return {"message": "Item deleted"}
