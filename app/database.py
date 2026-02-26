from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()