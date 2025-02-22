from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .views import router as views_router
from .apis import router as apis_router
import os

app = FastAPI(title="Technical Skills Registry API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static_dir = "/home/xan/hackudc/HACKUDC25/frontend/static"
static_dir = "../../frontend/static"
# templates_dir = "/home/xan/hackudc/HACKUDC25/frontend/templates"
templates_dir = "../../frontend/templates"

# # Print absolute paths for debugging
# print("Static directory absolute path:", os.path.abspath(static_dir))
# print("Templates directory absolute path:", os.path.abspath(templates_dir))

# # Ensure the directories exist
if not os.path.exists(static_dir):
    raise RuntimeError(f"Directory '{static_dir}' does not exist")
if not os.path.exists(templates_dir):
    raise RuntimeError(f"Directory '{templates_dir}' does not exist")

# Serve static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory=templates_dir)

# Include routers
app.include_router(views_router)
app.include_router(apis_router)

