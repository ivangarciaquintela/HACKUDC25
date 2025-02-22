from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..database.database import Base
from sqlalchemy.orm import relationship

class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    version = Column(String)
    description = Column(Text)
    category = Column(String)

    users = relationship("User", secondary="user_skills", back_populates="skills")
    issues = relationship("Issue", back_populates="skill")
    guides = relationship("Guide", back_populates="skill")	