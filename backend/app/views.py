from fastapi import APIRouter, Depends, HTTPException, status, Form, Header, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database.database import get_db
from .models.user import User
from .apis import get_current_user
from passlib.context import CryptContext
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="/home/xan/hackudc/HACKUDC25/frontend/templates")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db), authorization: str = Header(None)):
    try:
        current_user = await get_current_user(authorization, db)
        return templates.TemplateResponse("index.html", {"request": request, "user": current_user})
    except HTTPException:
        return templates.TemplateResponse("auth.html", {"request": request})
