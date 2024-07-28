from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

class Item(BaseModel):
    name: str

items = []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "items": items})

@app.post("/add/")
async def add_item(name: str = Form(...)):
    items.append(Item(name=name))
    return {"message": "Item added"}

@app.post("/delete/")
async def delete_item(name: str = Form(...)):
    global items
    items = [item for item in items if item.name != name]
    return {"message": "Item deleted"}
