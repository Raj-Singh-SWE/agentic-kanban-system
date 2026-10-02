from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import TaskDB
from backend.services.ai_engine import analyze_tasks

router = APIRouter()

@router.get("/insights/")
@router.get("/insights")
@router.post("/insights/")
@router.post("/insights")
def get_insights(db: Session = Depends(get_db)):
    db_tasks = db.query(TaskDB).all()
    tasks = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
        }
        for t in db_tasks
    ]
    
    return analyze_tasks(tasks)
