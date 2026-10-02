# Backward compatibility proxy: forwards to backend.main:app
import sys
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.main import app, engine, Base
from backend.database import get_db

__all__ = ["app", "engine", "Base", "get_db"]
