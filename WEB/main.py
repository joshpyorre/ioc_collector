from fastapi import FastAPI, APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from routes import base, map
# import uvicorn

router = APIRouter()
templates = Jinja2Templates(directory="templates")


app = FastAPI()
app.include_router(base.router)
app.include_router(map.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)