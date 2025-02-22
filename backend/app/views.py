from fastapi import APIRouter, Depends, HTTPException, status, Form, Header, Request
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

print('Views setup complete.')  # Debug print

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# @router.get("/", response_class=HTMLResponse)
# async def read_root(request: Request, db: Session = Depends(get_db), authorization: str = Header(None)):
#     # Debug prints
#     print(f"Checking if directory exists: {templates_dir}")
#     print(f"Absolute path: {os.path.abspath(templates_dir)}")
#     print(f"Directory exists: {os.path.exists(templates_dir)}")
#     print(f"Directory is readable: {os.access(templates_dir, os.R_OK)}")

#     try:
#         current_user = await get_current_user(authorization, db)
#         return templates.TemplateResponse("index.html", {"request": request, "user": current_user})
#     except HTTPException:
#         return RedirectResponse(url="/auth")

@router.get("/auth", response_class=HTMLResponse)
async def auth(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

print('Views loaded.')  # Debug print
