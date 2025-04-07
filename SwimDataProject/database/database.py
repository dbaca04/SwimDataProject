"""
Database Connection Module

This module handles database connections and provides a session factory.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables or use a default SQLite database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///swim_data.db')

# Create engine and session factory
engine = create_engine(DATABASE_URL, echo=False)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

# Base class for models
Base = declarative_base()


def get_db_session():
    """
    Get a database session.
    
    Returns:
        sqlalchemy.orm.Session: A new database session
    """
    return Session()


@contextmanager
def db_session():
    """
    Context manager for database sessions.
    
    Yields:
        sqlalchemy.orm.Session: A database session
        
    Example:
        with db_session() as session:
            swimmers = session.query(Swimmer).all()
    """
    session = get_db_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def init_db():
    """
    Initialize the database by creating all tables.
    """
    from .models import Base
    Base.metadata.create_all(engine)


def drop_db():
    """
    Drop all tables from the database.
    
    Warning: This will delete all data!
    """
    from .models import Base
    Base.metadata.drop_all(engine)
