import datetime
import json

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from tinydb import TinyDB

from app import covid


class PredictionData(BaseModel):
    user: str
    description: str
    confidence: float


class Prediction(BaseModel):
    id: int
    data: PredictionData


templates = Jinja2Templates(directory='website/')


async def predictions_homepage(request):
    predictions = [Prediction.parse_obj(d) for d in request.app.state.db.all()]
    return templates.TemplateResponse('predictions/index.html', {
        'request': request,
        'predictions': predictions,
    })


async def homepage(request):
    return templates.TemplateResponse('charts/index.html', {
        'request': request,
        'title': 'Covid charts',
    })


app = FastAPI(routes=[
    Route('/predictions/index.html', predictions_homepage),
    Route('/index.html', homepage),
    Mount('/static', StaticFiles(directory='website/static'), name='static')
])
app.state.db = TinyDB('db.json')


@app.post('/predictions')
async def create_prediction(data: PredictionData):
    prediction = Prediction(
        id=app.state.db.count(lambda x: True), data=data,
    )
    app.state.db.insert(prediction.dict())
    return {'message': 'Prediction added'}


@app.get('/predictions')
async def get_predictions():
    predictions = [Prediction.parse_obj(d) for d in app.state.db.all()]
    return {
        'predictions': predictions,
    }

@app.get('/data')
async def get_data(start: str):
    start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    data: pd.DataFrame = covid.get_latest_data(start_date=start_date)
    data_dict = json.loads(data.to_json(date_format='epoch'))
    return data_dict
