from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .views import router as views_router
from .apis import router as apis_router
import os

print('Starting application...')  # Debug print

app = FastAPI(title="Technical Skills Registry API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

# Serve static files
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# Configure Jinja2 templates
# templates = Jinja2Templates(directory=templates_dir)

# Include routers
app.include_router(views_router)
app.include_router(apis_router)

# Add the main router to the app
app.include_router(router)

print('Application is running.')  # Debug print

