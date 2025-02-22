from fastapi import FastAPI, Depends, HTTPException, status, Form, Header, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, text, func
from passlib.context import CryptContext
from datetime import datetime
from typing import Optional, List
from .database.database import get_db
from .models.user import User
from .models.skill import Skill
from .models.user_skill import UserSkill

app = FastAPI(title="Technical Skills Registry API")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to get current user
async def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    token = authorization.split(" ")[1]
    
    # Simple token validation - just check if a user with this username exists
    user = db.query(User).filter(User.username == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return user

@app.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = pwd_context.hash(password)
    db_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        created_at=datetime.now()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully"}

@app.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "access_token": user.username,
        "token_type": "bearer"
    }

@app.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email
    }

@app.put("/profile")
async def update_profile(
    email: str = Form(...),
    new_password: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if email is taken by another user
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Update user
    current_user.email = email
    if new_password:
        current_user.password_hash = pwd_context.hash(new_password)
    
    db.commit()
    return {"message": "Profile updated successfully"}

@app.get("/")
async def root():
    return {"message": "Welcome to Technical Skills Registry API"}

@app.get("/skills/search")
async def search_skills(
    q: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        Skill.id,
        Skill.name,
        Skill.version,
        Skill.description,
        Skill.category,
        func.count(UserSkill.user_id.distinct()).label('user_count')
    ).outerjoin(UserSkill)
    
    if q:
        query = query.filter(or_(
            Skill.name.ilike(f"%{q}%"),
            Skill.description.ilike(f"%{q}%")
        ))
    
    if category:
        query = query.filter(Skill.category == category)
    
    query = query.group_by(
        Skill.id,
        Skill.name,
        Skill.version,
        Skill.description,
        Skill.category
    )
    
    results = query.all()
    return [dict(zip(['id', 'name', 'version', 'description', 'category', 'user_count'], r)) for r in results]

@app.get("/skills/{skill_id}/users")
async def get_skill_users(
    skill_id: str,
    db: Session = Depends(get_db)
):
    users = db.query(
        User.username,
        UserSkill.proficiency_level,
        UserSkill.years_experience,
        UserSkill.last_used_date
    ).join(
        UserSkill,
        User.id == UserSkill.user_id
    ).filter(
        UserSkill.skill_id == skill_id
    ).all()
    
    return [
        {
            "username": user.username,
            "proficiency_level": user.proficiency_level,
            "years_experience": user.years_experience,
            "last_used_date": user.last_used_date
        }
        for user in users
    ]

@app.get("/skills/categories")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Skill.category).distinct().all()
    return [c[0] for c in categories if c[0]]

@app.get("/skills/{skill_id}")
async def get_skill_details(skill_id: str, db: Session = Depends(get_db)):
    skill = db.query(
        Skill.id,
        Skill.name,
        Skill.version,
        Skill.description,
        Skill.category,
        func.count(UserSkill.user_id.distinct()).label('user_count'),
        func.avg(UserSkill.proficiency_level).label('avg_proficiency'),
        func.avg(UserSkill.years_experience).label('avg_experience')
    ).outerjoin(UserSkill).filter(Skill.id == skill_id).group_by(
        Skill.id,
        Skill.name,
        Skill.version,
        Skill.description,
        Skill.category
    ).first()
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return dict(zip(
        ['id', 'name', 'version', 'description', 'category', 'user_count', 'avg_proficiency', 'avg_experience'],
        skill
    ))

@app.get("/users/{username}")
async def get_user_profile(username: str, db: Session = Depends(get_db)):
    user = db.query(
        User.username,
        User.email,
        User.created_at
    ).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at
    }

@app.get("/users/{username}/skills")
async def get_user_skills(username: str, db: Session = Depends(get_db)):
    user_skills = db.query(
        Skill.id.label('skill_id'),
        Skill.name,
        Skill.version,
        Skill.category,
        UserSkill.proficiency_level,
        UserSkill.years_experience,
        UserSkill.last_used_date
    ).join(
        UserSkill, Skill.id == UserSkill.skill_id
    ).join(
        User, User.id == UserSkill.user_id
    ).filter(
        User.username == username
    ).order_by(
        Skill.category,
        Skill.name
    ).all()
    
    return [
        {
            "skill_id": skill.skill_id,
            "name": skill.name,
            "version": skill.version,
            "category": skill.category,
            "proficiency_level": skill.proficiency_level,
            "years_experience": skill.years_experience,
            "last_used_date": skill.last_used_date
        }
        for skill in user_skills
    ] 
