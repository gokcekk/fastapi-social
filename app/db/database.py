# app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This is the path for our SQLite database file.
# "sqlite:///./social_network.db" means:
# - Use SQLite as the database engine
# - Create or use a file called "social_network.db"
# - The file will be in the same folder where you run uvicorn (project root)
SQLALCHEMY_DATABASE_URL = "sqlite:///./social.db"


# The engine is the core connection object for SQLAlchemy.
# It knows:
# - Which database to talk to (via the URL above)
# - How to open connections
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # For SQLite, this option is needed when using the database
    # from multiple threads, for example with FastAPI.
    connect_args={"check_same_thread": False},
)

"""
    SessionLocal is a "factory" that will create Session objects.
    Each Session is a "conversation" with the database.
    autocommit=False: We control when to commit manually.
    autoflush=False: Changes are not sent to the database automatically,
                 we control when to flush or commit.
"""

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# Base is the parent class for all ORM models.
# Every model class (for example User) will inherit from Base.
# SQLAlchemy uses this to know which tables to create.
Base = declarative_base()


def get_db():
    """
    Dependency used in FastAPI to provide a database session.

    How it works in a path operation:
    - FastAPI calls get_db and creates a SessionLocal instance.
    - The session is yielded to the path function
      (for example, def register(..., db: Session = Depends(get_db))).
    - After the request is handled, the "finally" block runs
      and the session is closed.
    """
    db = SessionLocal()
    try:
        # Give the database session to the caller (FastAPI will handle the yield)
        yield db
    finally:
        # Important: close the session so that connections are released.
        db.close()
