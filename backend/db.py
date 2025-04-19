import os

from app.repositories.user_repo import create_default_roles
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv("backend/.env")
DATABASE_USER = os.getenv("DB_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DB_PASS", "jain254p*")
DATABASE_NAME = os.getenv("DB_NAME", "mydb")
DATABASE_SOCKET = os.getenv("DB_SOCKET", "localhost:5432")
DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_SOCKET}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        create_default_roles(db)
        yield db
    finally:
        db.close()
