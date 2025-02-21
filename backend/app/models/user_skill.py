from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from ..database.database import Base

class UserSkill(Base):
    __tablename__ = "user_skills"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
    proficiency_level = Column(Integer)
    years_experience = Column(Float)
    last_used_date = Column(Date) 