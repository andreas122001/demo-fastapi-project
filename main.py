from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from functools import lru_cache
from pydantic import BaseModel
import transformers
from dataclasses import dataclass
import http3
import json

# Setup http3 client for external APIs
api = http3.AsyncClient()

# Setup logger
logger = logging.getLogger()
logger.handlers = [logging.StreamHandler()]
logger.setLevel(logging.INFO)

# Init FastAPI and jinja
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

# =====CLASSES===== #
class User(BaseModel):
    username: str
    password: str

    def __str__(self) -> str:
        return f"{self.username, self.password}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.username == other.username

# Dummy db
db = [
    User(username="andrebw", password="123")
]

# ===INDEX=== #
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context, status_code=200)

@app.get("/meme")
async def call_meme_api():
    logger.info("Meme requested")
    res = await api.get("http://meme-api.com/gimme")
    data = json.loads(res.text)
    logger.info(f"Meme url: {data['url']}")
    return HTMLResponse(content=f'<img src="{data["url"]}" alt="meme" width="500" height="600">')


# ===LOGIN=== #
@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("login.html", context, status_code=200)

@app.post("/login")
def do_login(username: Annotated[str, Form(...)], password: Annotated[str, Form(...)]):
    user = User(username=username, password=password)
    logger.info(f"User login: {user}")

    if user not in db:
        logger.info("User not found")
        return Response(status_code=401)
    if db[db.index(user)].password != user.password:
        logger.info("Incorrect password")
        return Response(status_code=401)
    
    return Response(status_code=200)


# ===REGISTRATION=== #
@app.post("/register")
def put_in_db(username: Annotated[str, Form(...)], password: Annotated[str, Form(...)]):
    user = User(username=username, password=password)
    logger.info(f"Register user {user}")

    if user in db:
        logger.info(f"user already exists: {user}")
        return Response(status_code=409)
    
    db.append(user)

    return Response(status_code=200)


@app.post("/ml/init")
def initialize_ml_model():
    load_model()
    return Response(status_code=200)


# ===INFERENCE=== #
@app.post("/ml/inference")
def inference(data: str):
    model = load_model()
    return model(data)




@lru_cache() # loads model to cache and return cached value
def load_model():
    # logger.info("Loading ML model...")
    # pipeline = transformers.pipeline("text-classification", model="andreas122001/roberta-wiki-detector")
    return



