from fastapi import APIRouter, Depends, HTTPException, status, Form, Header, Request, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database.database import get_db
from .models.user import User
from .apis import get_current_user
from passlib.context import CryptContext
from datetime import datetime
import os

router = APIRouter()
templates_dir = "/app/templates"

if not os.path.exists(templates_dir):
    raise RuntimeError(f"Directory '{templates_dir}' does not exist")
templates = Jinja2Templates(directory=templates_dir)


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def check_auth(request: Request, db: Session) -> User | None:
    token = request.cookies.get("access_token")
    print(f"Debug - Got token from cookies: {token}")  # Debug line
    
    if not token:
        return None
        
    try:
        user = await get_current_user(token, db)
        print(f"Debug - User found: {user}")  # Debug line
        return user
    except HTTPException as e:
        print(f"Debug - Auth error: {str(e)}")  # Debug line
        return None

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    user = await check_auth(request, db)
    if not user:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@router.get("/auth", response_class=HTMLResponse)
async def auth(request: Request, db: Session = Depends(get_db)):
    user = await check_auth(request, db)
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("auth.html", {"request": request})

@router.get("/users", response_class=HTMLResponse)
async def users(request: Request, db: Session = Depends(get_db)):
    user = await check_auth(request, db)
    if not user:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("users.html", {"request": request, "user": user})

@router.get("/guides", response_class=HTMLResponse)
async def guides(request: Request, db: Session = Depends(get_db)):
    user = await check_auth(request, db)
    if not user:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("guides.html", {"request": request, "user": user})

@router.get("/issues", response_class=HTMLResponse)
async def issues(request: Request, db: Session = Depends(get_db)):
    user = await check_auth(request, db)
    if not user:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("issues.html", {"request": request, "user": user})

@router.get("/issues/manage", response_class=HTMLResponse)  # Changed from /manage-issues
async def manage_issues(request: Request, db: Session = Depends(get_db)):
    user = await check_auth(request, db)
    if not user:
        return RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("manage-issues.html", {"request": request, "user": user})

@router.get("/skills", response_class=HTMLResponse)
async def guides(request: Request):
    return templates.TemplateResponse("skills.html", {"request": request})

@router.get("/myProfile", response_class=HTMLResponse)
async def guides(request: Request):
    return templates.TemplateResponse("myProfile.html", {"request": request})

@router.get("/agent", response_class=HTMLResponse)
async def guides(request: Request):
    return templates.TemplateResponse("agent.html", {"request": request})

