import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

# Handle missing DATABASE_URL - use SQLite as fallback for testing
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./topfloor_dev.db"
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}  # SQLite specific
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL query logging in development
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,  # Number of connections to maintain in the pool
        max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
