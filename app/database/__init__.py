"""
Database Connection Module
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base_class import Base

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root@localhost/hearme_learning"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine) 