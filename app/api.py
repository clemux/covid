import datetime
import json

import pandas as pd
from app import covid
from app.db import crud, schemas
from app.db.database import SessionLocal, Session
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from tinydb import TinyDB



templates = Jinja2Templates(directory='website/')


async def homepage(request):
    return templates.TemplateResponse('charts/index.html', {
        'request': request,
        'title': 'Covid charts',
    })


app = FastAPI(routes=[
    Route('/index.html', homepage),
    Mount('/static', StaticFiles(directory='website/static'), name='static')
])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/data', response_model=list[schemas.Cases])
async def get_data(start: datetime.date, db: Session = Depends(get_db)):
    cases = crud.get_cases(db, start_date=start)

    return cases
