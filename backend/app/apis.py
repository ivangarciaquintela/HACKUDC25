from fastapi import APIRouter, Depends, HTTPException, status, Header, Query, Form
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from .database.database import get_db
from .models.skill import Skill
from .models.user_skill import UserSkill
from .models.user import User
from .models.guide import Guide
from .models.issue import Issue
from .models.issue import Comment
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from .agents.db_agent import db_agent
from .agents.issue_agent import issue_creation_agent
from .agents.guide_agent import guide_creation_agent

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = "your-secret-key-here"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Helper function to get current user
async def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(authorization, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception
    return user

@router.post("/register")
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

@router.post("/login")
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
    
    access_token = create_access_token(data={"sub": user.username})
    
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access
        secure=True,    # Only send over HTTPS
        samesite="lax", # CSRF protection
        max_age=1800    # 30 minutes
    )
    return response

@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/auth", status_code=status.HTTP_303_SEE_OTHER)
    
    # Clear all possible authentication cookies
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="lax"
    )
    response.delete_cookie(
        key="session",
        path="/",
        secure=True,
        httponly=True,
        samesite="lax"
    )
    response.delete_cookie(
        key="Authorization",
        path="/",
        secure=True,
        httponly=True,
        samesite="lax"
    )
    
    # Also set cookies to expire immediately as a backup
    response.set_cookie(
        key="access_token",
        value="",
        expires=0,
        max_age=0,
        path="/"
    )
    
    return response

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email
    }

@router.put("/profile")
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

@router.get("/")
async def root():
    return {"message": "Welcome to Technical Skills Registry API"}

@router.get("/skills/search")
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

@router.get("/skills/{skill_name}/versions")
async def get_skill_versions(skill_name: str, db: Session = Depends(get_db)):
    versions = db.query(Skill.version).filter(Skill.name == skill_name).distinct().all()
    return [v[0] for v in versions if v[0]]

@router.get("/skills/{skill_id}/users")
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

@router.get("/skills/{skill_id}/guides")
async def get_skill_guides(
    skill_id: str,
    db: Session = Depends(get_db)
):
    guides = db.query(
        Guide.id,
        Guide.title,
        Guide.content,
        Guide.created_at,
        User.id.label("user_id"),
        User.username
    ).join(
        User, Guide.user_id == User.id
    ).filter(
        Guide.skill_id == skill_id
    ).all()
    
    return [
        {
            "id": guide.id,
            "title": guide.title,
            "content": guide.content,
            "created_at": guide.created_at,
            "user_id": guide.user_id,
            "username": guide.username
        }
        for guide in guides
    ]

@router.get("/skills/{skill_id}/issues")
async def get_skill_issues(
    skill_id: str,
    db: Session = Depends(get_db)
):
    issues = db.query(
        Issue.id,
        Issue.title,
        Issue.description,
        Issue.created_at,
        User.id.label("user_id"),
        User.username
    ).join(
        User, Issue.user_id == User.id
    ).filter(
        Issue.skill_id == skill_id
    ).all()
    
    return [
        {
            "id": issue.id,
            "title": issue.title,
            "description": issue.description,
            "created_at": issue.created_at,
            "user_id": issue.user_id,
            "username": issue.username
        }
        for issue in issues
    ]

@router.get("/skills/categories")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Skill.category).distinct().all()
    return [c[0] for c in categories if c[0]]

@router.get("/skills/{skill_id}")
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

@router.get("/users/search")
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

@router.get("/users/{username}")
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

@router.get("/users/{username}/skills")
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

@router.post("/users/{username}/skills")
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

@router.delete("/users/{username}/skills/{skill_id}")
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

@router.post("/agent/query")
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

@router.get("/users/{username}/issues")
async def get_user_issues(
    username: str,
    db: Session = Depends(get_db)
):
    # Get the user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    issues = db.query(
        Issue.id,
        Issue.title,
        Issue.description,
        Issue.created_at,
        Skill.name.label('skill_name'),
        Skill.version.label('skill_version')
    ).join(
        Skill, Issue.skill_id == Skill.id
    ).filter(
        Issue.user_id == user.id
    ).order_by(
        Issue.created_at.desc()
    ).all()

    return [
        {
            "id": str(issue.id),
            "title": issue.title,
            "description": issue.description,
            "created_at": issue.created_at,
            "skill_name": issue.skill_name,
            "skill_version": issue.skill_version
        }
        for issue in issues
    ]

@router.post("/users/{username}/issues")
async def create_user_issue(
    username: str,
    issue_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user is creating their own issue
    if username != current_user.username:
        raise HTTPException(
            status_code=403,
            detail="You can only create issues for yourself"
        )

    # Get the skill
    skill = db.query(Skill).filter(
        Skill.id == issue_data['skill_id'],
        Skill.version == issue_data['skill_version']
    ).first()

    if not skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

    # Create new issue
    new_issue = Issue(
        title=issue_data['title'],
        description=issue_data['description'],
        skill_id=skill.id,
        user_id=current_user.id
    )

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return {
        "message": "Issue created successfully",
        "id": str(new_issue.id)
    }

@router.delete("/users/{username}/issues/{issue_id}")
async def delete_user_issue(
    username: str,
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user is deleting their own issue
    if username != current_user.username:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own issues"
        )

    # Find the issue
    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.user_id == current_user.id
    ).first()

    if not issue:
        raise HTTPException(
            status_code=404,
            detail="Issue not found"
        )

    # Delete the issue
    db.delete(issue)
    db.commit()

    return {"message": "Issue deleted successfully"}

@router.get("/users/{username}/guides")
async def get_user_guides(
    username: str,
    db: Session = Depends(get_db)
):
    # Get the user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    guides = db.query(
        Guide.id,
        Guide.title,
        Guide.content,
        Guide.created_at,
        Skill.name.label('skill_name'),
        Skill.version.label('skill_version')
    ).join(
        Skill, Guide.skill_id == Skill.id
    ).filter(
        Guide.user_id == user.id
    ).order_by(
        Guide.created_at.desc()
    ).all()

    return [
        {
            "id": str(guide.id),
            "title": guide.title,
            "content": guide.content,
            "created_at": guide.created_at,
            "skill_name": guide.skill_name,
            "skill_version": guide.skill_version
        }
        for guide in guides
    ]

@router.post("/users/{username}/guides")
async def create_user_guide(
    username: str,
    guide_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user is creating their own guide
    if username != current_user.username:
        raise HTTPException(
            status_code=403,
            detail="You can only create guides for yourself"
        )

    # Get the skill
    skill = db.query(Skill).filter(
        Skill.id == guide_data['skill_id'],
        Skill.version == guide_data['skill_version']
    ).first()

    if not skill:
        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

    # Create new guide
    new_guide = Guide(
        title=guide_data['title'],
        content=guide_data['content'],
        skill_id=skill.id,
        user_id=current_user.id
    )

    db.add(new_guide)
    db.commit()
    db.refresh(new_guide)

    return {
        "message": "Guide created successfully",
        "id": str(new_guide.id)
    }

@router.delete("/users/{username}/guides/{guide_id}")
async def delete_user_guide(
    username: str,
    guide_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user is deleting their own guide
    if username != current_user.username:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own guides"
        )

    # Find the guide
    guide = db.query(Guide).filter(
        Guide.id == guide_id,
        Guide.user_id == current_user.id
    ).first()

    if not guide:
        raise HTTPException(
            status_code=404,
            detail="Guide not found"
        )

    # Delete the guide
    db.delete(guide)
    db.commit()

    return {"message": "Guide deleted successfully"}

@router.get("/guides/{guide_id}")
async def get_guide_details(guide_id: str, db: Session = Depends(get_db)):
    guide = db.query(
        Guide.id,
        Guide.title,
        Guide.content,
        Guide.created_at,
        Skill.name.label('skill_name'),
        Skill.version.label('skill_version'),
        User.username
    ).join(
        Skill, Guide.skill_id == Skill.id
    ).join(
        User, Guide.user_id == User.id
    ).filter(
        Guide.id == guide_id
    ).first()

    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")

    return {
        "id": str(guide.id),
        "title": guide.title,
        "content": guide.content,
        "created_at": guide.created_at,
        "skill_name": guide.skill_name,
        "skill_version": guide.skill_version,
        "username": guide.username
    }

@router.get("/issues/{issue_id}")
async def get_issue_details(issue_id: str, db: Session = Depends(get_db)):
    issue = db.query(
        Issue.id,
        Issue.title,
        Issue.description,
        Issue.created_at,
        Skill.name.label('skill_name'),
        Skill.version.label('skill_version'),
        User.username
    ).join(
        Skill, Issue.skill_id == Skill.id
    ).join(
        User, Issue.user_id == User.id
    ).filter(
        Issue.id == issue_id
    ).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return {
        "id": str(issue.id),
        "title": issue.title,
        "description": issue.description,
        "created_at": issue.created_at,
        "skill_name": issue.skill_name,
        "skill_version": issue.skill_version,
        "username": issue.username
    }

class NaturalLanguageIssueRequest(BaseModel):
    description: str

@router.post("/agent/create_issue")
async def create_issue_with_agent(
    request: NaturalLanguageIssueRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to create a new issue using natural language through an AI agent.
    The agent will extract the necessary information and create the issue.
    
    Args:
        request: NaturalLanguageIssueRequest containing the natural language description
        current_user: The authenticated user creating the issue
        
    Returns:
        The agent's response containing the created issue details
    """
    try:
        # Add user context to the request
        augmented_request = f"User '{current_user.id}' wants to create an issue: {request.description}"
        response = issue_creation_agent.run(augmented_request)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating issue: {str(e)}"
        )

class NaturalLanguageGuideRequest(BaseModel):
    description: str

@router.post("/agent/create_guide")
async def create_guide_with_agent(
    request: NaturalLanguageGuideRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to create a new learning guide using natural language through an AI agent.
    The agent will structure the content and create a well-organized guide.
    
    Args:
        request: NaturalLanguageGuideRequest containing the natural language description
        current_user: The authenticated user creating the guide
        
    Returns:
        The agent's response containing the created guide details
    """
    try:
        # Add user context to the request
        augmented_request = f"User '{current_user.id}' wants to create a guide: {request.description}"
        response = guide_creation_agent.run(augmented_request)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating guide: {str(e)}"
        )

@router.get("/issues/{issue_id}/comments")
async def get_issue_comments(issue_id: str, db: Session = Depends(get_db)):
    comments = db.query(
        Comment.id,
        Comment.content,
        Comment.created_at,
        User.username
    ).join(
        User, Comment.user_id == User.id
    ).filter(
        Comment.issue_id == issue_id
    ).order_by(
        Comment.created_at.asc()
    ).all()

    return [
        {
            "id": str(comment.id),
            "content": comment.content,
            "created_at": comment.created_at,
            "username": comment.username
        }
        for comment in comments
    ]

@router.post("/issues/{issue_id}/comments")
async def create_issue_comment(
    issue_id: str,
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=404,
            detail="Issue not found"
        )

    # Create new comment
    new_comment = Comment(
        content=content,
        issue_id=issue_id,
        user_id=current_user.id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {
        "id": str(new_comment.id),
        "content": new_comment.content,
        "created_at": new_comment.created_at,
        "username": current_user.username
    }