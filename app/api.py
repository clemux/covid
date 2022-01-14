from fastapi import FastAPI
from pydantic import BaseModel
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from tinydb import TinyDB


class PredictionData(BaseModel):
    user: str
    description: str
    confidence: float


class Prediction(BaseModel):
    id: int
    data: PredictionData


templates = Jinja2Templates(directory='website/predictions/')


async def homepage(request):
    predictions = [Prediction.parse_obj(d) for d in request.app.state.db.all()]
    return templates.TemplateResponse('index.html', {
        'request': request,
        'predictions': predictions,
    })


app = FastAPI(routes=[
    Route('/', homepage),
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
