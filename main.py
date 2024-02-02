from typing import Annotated
from fastapi import FastAPI, Request, Form, HTTPException
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
import time
import asyncio

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
    User(username="user", password="user"),
    User(username="admin", password="admin")
]

# ===INDEX=== #
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context, status_code=200)


# ===MEME=== #
@app.get("/meme", response_class=HTMLResponse)
def mem(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("meme.html", context, status_code=200)

@app.get("/get-meme")
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
        return HTMLResponse("<div id='error' hx-swap-oob='true'>Login failed!</div>")
        # return HTMLResponse("<div id='error' hx-swap-oob='true'>Login failed!</div>", status_code=401)
    if db[db.index(user)].password != user.password:
        logger.info("Incorrect password")
        return HTMLResponse("<div id='error' hx-swap-oob='true'>Login failed!</div>")

    return Response("Login Successful!", status_code=200)


# ===REGISTRATION=== #
@app.get("/register", response_class=HTMLResponse)
def get_login_page(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("register.html", context, status_code=200)

@app.post("/register")
def put_in_db(username: Annotated[str, Form(...)], password: Annotated[str, Form(...)]):
    user = User(username=username, password=password)
    logger.info(f"Register user {user}")

    if user in db:
        logger.info(f"user already exists: {user}")
        return HTMLResponse("<div id='error' hx-swap-oob='true'>User already exists!</div>")
    
    db.append(user)

    return Response("User registered!", status_code=200)


# ===MACHINE LEARNING=== #

# This is fine for now
model = None # ml model
task = None # model-loading task

@app.get("/ml")
def get_ml_page(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("ml.html", context, status_code=200)

@app.post("/ml/init")
async def initialize_ml_model():
    global model, task
    if not model and not task:
        task = asyncio.create_task(load_model())
        return HTMLResponse("""        
            <div
                hx-post="/ml/init"
                hx-trigger="load delay:2s"
                hx-swap="outerHTML">
            Loading model...
            </div>
            """)
    else:
        return Response("Model ready!")

@app.post("/ml/inference")
def inference(data: str):
    global model
    res = model(data)
    return HTMLResponse(f"<div> Prediction: {res.label} <br> </div>")

# Helpers
async def load_model():
    global model
    if not model:
        logger.info("Loading ML model...")
        model = await load_model_cache()
    logger.info(f"Model loaded!")

@lru_cache() # loads model to cache and return cached value
async def load_model_cache():
    logger.info("Retrieving ML model...")
    pipeline = await asyncio.create_task(transformers.pipeline("text-classification", model="andreas122001/roberta-wiki-detector"))
    return pipeline



