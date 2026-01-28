"""
Database session management.

This module handles database connection configuration and provides
a session factory for database operations. It uses environment variables
for database connection settings.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Hardcoded database URL for Supabase pooler connection
# TODO: Move this to environment variables later
DATABASE_URL = "postgresql://postgres.uhloeqddpdravorocpfm:Frelosystems13131.@aws-1-eu-central-2.pooler.supabase.com:6543/postgres"

# Create SQLAlchemy engine
# Configured for Supabase pooler connection
# pool_pre_ping=True ensures connections are alive before using them
# pool_size and max_overflow configured for pooled connections
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Number of connections to maintain in the pool
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create session factory
# autocommit=False: Transactions must be explicitly committed
# autoflush=False: Changes aren't automatically flushed to DB
# bind=engine: Sessions are bound to our database engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.
    
    This function provides a database session that automatically closes
    after the request is complete. Use it with FastAPI's Depends() to
    inject database sessions into route handlers.
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
