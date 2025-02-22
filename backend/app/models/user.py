from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..database.database import Base
from sqlalchemy.orm import relationship
# Ensure all dependent classes are imported
from .skill import Skill
from .issue import Issue, Comment
from .guide import Guide

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True))

    skills = relationship("Skill", secondary="user_skills", back_populates="users")
    issues = relationship("Issue", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    guides = relationship("Guide", back_populates="user")