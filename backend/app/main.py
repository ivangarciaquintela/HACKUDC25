from fastapi import FastAPI, Depends, HTTPException, status, Form, Header, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, text, func
from passlib.context import CryptContext
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .database.database import get_db
from .models.user import User
from .models.skill import Skill
from .models.user_skill import UserSkill
from .agents.db_agent import db_agent

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

@app.get("/skills/{skill_name}/versions")
async def get_skill_versions(skill_name: str, db: Session = Depends(get_db)):
    versions = db.query(Skill.version).filter(Skill.name == skill_name).distinct().all()
    return [v[0] for v in versions if v[0]]

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

@app.get("/users/search")
async def search_users(
    q: Optional[str] = None,
    skill: Optional[str] = None,
    min_level: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # Start with base query
    query = db.query(
        User.username,
        User.created_at,
        func.count(UserSkill.skill_id).label('total_skills')
    ).outerjoin(UserSkill)
    
    # Apply search filter
    if q:
        query = query.filter(User.username.ilike(f"%{q}%"))
    
    # First group to get total skills
    query = query.group_by(User.id, User.username, User.created_at)
    
    # Execute main query
    users = query.all()
    
    # For each user, get their top skills
    result = []
    for user in users:
        # Get top skills for user (highest proficiency)
        top_skills_query = db.query(
            Skill.name,
            UserSkill.proficiency_level
        ).join(
            UserSkill, Skill.id == UserSkill.skill_id
        ).join(
            User, User.id == UserSkill.user_id
        ).filter(
            User.username == user.username
        )
        
        # Apply skill filter if provided
        if skill:
            top_skills_query = top_skills_query.filter(Skill.name == skill)
        
        # Apply minimum level filter if provided
        if min_level:
            top_skills_query = top_skills_query.filter(UserSkill.proficiency_level >= min_level)
            # Skip user if they don't meet the minimum level requirement
            if not top_skills_query.first():
                continue
        
        top_skills = top_skills_query.order_by(
            UserSkill.proficiency_level.desc()
        ).limit(3).all()
        
        # Skip user if they don't have the required skill
        if skill and not top_skills:
            continue
        
        result.append({
            "username": user.username,
            "created_at": user.created_at,
            "total_skills": user.total_skills,
            "top_skills": [
                {
                    "name": skill.name,
                    "proficiency_level": skill.proficiency_level
                }
                for skill in top_skills
            ]
        })
    
    return result

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

@app.post("/users/{username}/skills")
async def add_user_skill(
    username: str,
    skill_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user is modifying their own skills
    if username != current_user.username:
        raise HTTPException(
            status_code=403,
            detail="You can only modify your own skills"
        )
    
    # Check if we're adding an existing skill or creating a new one
    if 'skill_id' in skill_data:
        # Adding an existing skill
        skill = db.query(Skill).filter(Skill.id == skill_data['skill_id']).first()
        if not skill:
            raise HTTPException(
                status_code=404,
                detail="Skill not found"
            )
    else:
        # Creating a new skill
        # Check if skill exists with the same name and version
        skill = db.query(Skill).filter(
            Skill.name == skill_data['name'],
            Skill.version == skill_data['version']
        ).first()

        if not skill:
            # Create new skill with all provided information
            skill = Skill(
                name=skill_data['name'],
                version=skill_data['version'],
                category=skill_data['category'],
                description=skill_data['description']
            )
            db.add(skill)
            db.commit()
            db.refresh(skill)
    
    # Check if user already has this skill
    existing_skill = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_id == skill.id
    ).first()
    
    if existing_skill:
        raise HTTPException(
            status_code=400,
            detail="You already have this skill version"
        )
    
    # Add skill to user
    user_skill = UserSkill(
        user_id=current_user.id,
        skill_id=skill.id,
        proficiency_level=skill_data['proficiency_level'],
        years_experience=skill_data['years_experience'],
        last_used_date=datetime.now()
    )
    
    db.add(user_skill)
    db.commit()
    
    return {"message": "Skill added successfully"}

@app.delete("/users/{username}/skills/{skill_id}")
async def delete_user_skill(
    username: str,
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user is modifying their own skills
    if username != current_user.username:
        raise HTTPException(
            status_code=403,
            detail="You can only modify your own skills"
        )
    
    # Find and delete the user skill
    user_skill = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_id == skill_id
    ).first()
    
    if not user_skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )
    
    db.delete(user_skill)
    db.commit()
    
    return {"message": "Skill deleted successfully"}

class QueryRequest(BaseModel):
    query: str

@app.post("/agent/query")
async def query_agent(request: QueryRequest):
    """
    Endpoint to query the database using natural language through an AI agent.
    The agent will convert the natural language query into SQL and execute it.
    
    Args:
        request: QueryRequest containing the natural language query
        
    Returns:
        The agent's response containing the query results
    """
    try:
        response = db_agent.run(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )
