from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.config import db_settings

engine = create_engine(
    db_settings.DATABASE_URL,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 