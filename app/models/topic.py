from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    # Relationship với Vocabulary
    vocabularies = relationship("Vocabulary", back_populates="topic") 