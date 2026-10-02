import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure workspace root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from backend.database import engine, Base
    from backend.routers import tasks, ai
except ImportError:
    from database import engine, Base
    from routers import tasks, ai

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Productivity Dashboard API",
    description="FastAPI modular backend for task management and AI discipline coaching",
    version="2.0.0",
)

# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(ai.router, prefix="/ai", tags=["AI Insights"])

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": "AI Productivity Dashboard API",
        "endpoints": {
            "tasks": "/tasks/",
            "ai_insights": "/ai/insights/",
            "docs": "/docs",
        },
    }

# AWS Lambda Handler
from mangum import Mangum
handler = Mangum(app)
