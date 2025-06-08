from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite connection URL (using a local file database named app.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# SQLAlchemy engine to manage the connection to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal is a factory for creating new SQLAlchemy session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models (tables will inherit from this)
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.

    This function creates a new SQLAlchemy session, yields it for use in request handlers,
    and ensures the session is properly closed after the request is handled.

    Yields:
        Session: SQLAlchemy database session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
