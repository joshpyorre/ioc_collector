from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/images/favicon.ico")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
