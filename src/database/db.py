import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Resolve project root (two levels up from src/database/db.py)
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5438")
DB_NAME = os.getenv("POSTGRES_DB", "tshwane_bus")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

engine: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@contextmanager
def get_connection() -> Generator[Connection, None, None]:
    """Yield a transactional SQLAlchemy Core connection (for raw SQL or pandas)."""
    with engine.begin() as conn:
        yield conn


def run_safe_query(
    sql: str, params: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Execute a parameterized query inside a strict READ ONLY transaction."""
    with engine.connect() as conn:
        # Enforce read-only mode & 3s timeout at the session/transaction level
        conn.execute(text("SET TRANSACTION READ ONLY"))
        conn.execute(text("SET LOCAL statement_timeout = '3000ms'"))
        result = conn.execute(text(sql), params or {})
        return [dict(row._mapping) for row in result]


def get_db() -> Generator[Session, None, None]:
    """Yield an ORM session (compatible with FastAPI Depends or manual next())."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_connection() -> bool:
    """Verify database connectivity."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
