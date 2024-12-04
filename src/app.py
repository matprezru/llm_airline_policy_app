from fastapi import FastAPI, Request
import logging

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api.endpoints import query, database

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Include API routers
# API router for endpoints related to queries
app.include_router(query.router, prefix="/query", tags=["Query"])
# API router for endpoints related to database operations (upload, delete, list...)
app.include_router(database.router, prefix="/database", tags=["Database"])
    
# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Templates setup
templates = Jinja2Templates(directory="src/templates")

# Endpoint for serving the web interface
@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
