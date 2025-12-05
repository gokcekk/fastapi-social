# app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL for SQLAlchemy.
# "sqlite:///./social.db" means:
# - Use SQLite as the database engine.
# - Use a file called "social.db".
# - The file will be created/used in the project root (where you run uvicorn).
SQLALCHEMY_DATABASE_URL = "sqlite:///./social.db"

# The engine is the core connection object for SQLAlchemy.
# It is responsible for:
# - Knowing which database to connect to (via the URL above).
# - Managing the low-level DBAPI connections under the hood.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # For SQLite, this option is needed when using the database
    # from multiple threads (for example, with FastAPI's default settings).
    connect_args={"check_same_thread": False},
)

"""
SessionLocal is a "factory" that creates Session objects.

Each Session represents a single "conversation" with the database.

Options:
- autocommit=False:
    We decide when to commit transactions manually (db.commit()).
- autoflush=False:
    SQLAlchemy will not automatically flush changes to the database;
    we control when to flush/commit. This helps avoid unexpected queries.
"""
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# Base is the parent class for all ORM models.
# Every model class (for example, User) will inherit from Base.
# SQLAlchemy uses this to collect all models and create the corresponding tables.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session.

    Typical usage in a path operation:
        def some_endpoint(db: Session = Depends(get_db)):
            ...

    Flow:
    1. Create a new SessionLocal() instance.
    2. Yield it to the path operation function.
    3. After the request is handled, the "finally" block runs
       and the session is closed (important for releasing connections).
    """
    db = SessionLocal()
    try:
        # Yield the database session to the caller.
        # FastAPI will inject this into path operations that depend on get_db.
        yield db
    finally:
        # Always close the session after the request is done.
        db.close()
