from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..database.database import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    version = Column(String(50))
    description = Column(String)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    creator = relationship("User", back_populates="created_skills")
    users = relationship("User", secondary="user_skills", back_populates="skills") 