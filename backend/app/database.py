"""
Database connection and session management.

Uses SQLModel (built on SQLAlchemy) for ORM and connection pooling.
Connects to Neon PostgreSQL using DATABASE_URL from environment.
"""

from typing import Generator
from sqlmodel import Session, create_engine, SQLModel, text
from app.config import settings


# Create SQLModel engine with connection pooling
# echo=True in development shows SQL queries in logs
# SQLite doesn't support all pooling parameters
if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False}  # SQLite specific
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,  # Connection pool size
        max_overflow=10  # Allow up to 10 extra connections
    )


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Usage:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            items = session.exec(select(Item)).all()
            return items

    Yields:
        Session: SQLModel database session

    The session is automatically closed when the request completes.
    """
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """
    Initialize database connection.

    For SQLite (local testing): Creates all tables automatically
    For PostgreSQL (production): Uses Alembic migrations
    """
    # Import models to register them with SQLModel
    from app.models.user import User
    from app.models.task import Task

    try:
        # Create all tables (only works with SQLite for local testing)
        # In production with PostgreSQL, use Alembic migrations instead
        if "sqlite" in settings.DATABASE_URL:
            SQLModel.metadata.create_all(engine)
            print("[OK] SQLite database tables created")

        # Test database connection
        with Session(engine) as session:
            # Use text() for raw SQL queries
            session.exec(text("SELECT 1"))
        print("[OK] Database connection established")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        raise
