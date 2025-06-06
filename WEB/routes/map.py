from fastapi import APIRouter, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import HTTPException

from models import collection_geo
from utils import process_urls_multiprocessing, generate_map_data_and_statistics

router = APIRouter()
templates = Jinja2Templates(directory="templates")
    
@router.get("/geo_urls", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("map.html", {
        "request": request,
        "map_data": None,
        "failures": 0,
        "country_stats": None
    })

# This commented out part looked up only URLs:

# @router.post("/upload_urls_to_map", response_class=HTMLResponse)
# async def handle_upload(request: Request, file: UploadFile = File(...)):
#     try:
#         content = await file.read()
#         urls = content.decode('utf-8').splitlines()

#         results, failures = process_urls_multiprocessing(urls)
#         map_data, country_stats = generate_map_data_and_statistics(results)
#         sorted_country_stats = dict(sorted(country_stats.items(), key=lambda item: item[1], reverse=True))
        
#         chart_data = {
#             'labels': list(country_stats.keys()),
#             'values': list(country_stats.values())
#         }
#         return templates.TemplateResponse("map.html", {
#             "request": request,
#             "map_data": map_data,
#             "failures": failures,
#             "country_stats": sorted_country_stats,
#             "chart_data": chart_data
#         })
#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=400, detail="Failed to process the uploaded file.")

@router.post("/upload_urls_to_map", response_class=HTMLResponse)
async def handle_upload(request: Request, file: UploadFile = File(...)):
    try:
        content = await file.read()
        lines = content.decode('utf-8').splitlines()
        
        # Extract the second item from each line (index 1), skip invalid ones
        inputs = []
        for line in lines:
            parts = line.split(',')
            if len(parts) > 1:
                inputs.append(parts[1].strip())

        results, failures = process_urls_multiprocessing(inputs)
        map_data, country_stats = generate_map_data_and_statistics(results)
        sorted_country_stats = dict(sorted(country_stats.items(), key=lambda item: item[1], reverse=True))
        
        chart_data = {
            'labels': list(sorted_country_stats.keys()),
            'values': list(sorted_country_stats.values())
        }
        return templates.TemplateResponse("map.html", {
            "request": request,
            "map_data": map_data,
            "failures": failures,
            "country_stats": sorted_country_stats,
            "chart_data": chart_data
        })
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Failed to process the uploaded file.")

    
@router.get("/database-entries", response_class=HTMLResponse)
async def view_database_entries(request: Request):
    entries = list(collection_geo.find({"status": "success"}))
    map_data, country_stats = generate_map_data_and_statistics(entries)
    sorted_country_stats = dict(sorted(country_stats.items(), key=lambda item: item[1], reverse=True))

    chart_data = {
        'labels': list(sorted_country_stats.keys()),
        'values': list(sorted_country_stats.values())
    }
    return templates.TemplateResponse("database_entries.html", {
        "request": request,
        "map_data": map_data,
        "country_stats": sorted_country_stats,
        "chart_data": chart_data,
        "failures": len(list(collection_geo.find({"status": "failure"})))
    })