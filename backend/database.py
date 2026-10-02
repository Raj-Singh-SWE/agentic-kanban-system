from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Resolve productivity.db relative to the workspace project root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "productivity.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE.as_posix()}"

# check_same_thread=False is needed for FastAPI+SQLite concurrency.
# timeout=15 helps prevent 'database is locked' errors during rapid clicks.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False, "timeout": 15}
)

# Enable Write-Ahead Logging (WAL) for better concurrency
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# FastAPI DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
