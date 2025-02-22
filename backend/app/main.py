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
templates_dir = "/app/templates"

if not os.path.exists(templates_dir):
    raise RuntimeError(f"Directory '{templates_dir}' does not exist")
templates = Jinja2Templates(directory=templates_dir)

print('Application setup complete.')  # Debug print

@router.get("/mateo", response_class=HTMLResponse)
async def auth(request: Request):
    print('mateo.')  # Debug print
    return templates.TemplateResponse("auth.html", {"request": request})

# # Serve static files
# app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configure Jinja2 templates
# templates = Jinja2Templates(directory=templates_dir)

# Include routers
app.include_router(views_router)
app.include_router(apis_router)

print('Application is running.')  # Debug print

