from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import mysql.connector
from mysql.connector import Error

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/hearme_learning"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="hearme_learning"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None 