from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Vocabulary(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), nullable=False)
    meaning = Column(Text, nullable=False)
    video_url = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    # Nếu cần quan hệ với Topic
    topic = relationship("Topic", back_populates="vocabularies", lazy="joined") 