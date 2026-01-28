"""
SQLAlchemy base class for database models.

This module provides the declarative base class that all database models
should inherit from. It's used by SQLAlchemy to track model metadata and
generate database schemas.
"""

from sqlalchemy.orm import declarative_base

# Create the declarative base class
# All database models will inherit from this Base class
Base = declarative_base()
