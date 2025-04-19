from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import Column, String
from app.models.base import Base
from app.repositories.user_repo import create_default_roles


DATABASE_URL = "postgresql://postgres:kritika123@localhost:5432/mydb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        # Create default roles if they don't already exist
        create_default_roles(db)
        print("done")
        yield db
    finally:
        db.close()
