import datetime
from typing import List, Dict, Any

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Import local DB utilities and model
from .database import get_db
from .models import TaskDB

router = APIRouter()


# -----------------------------
# Helper / engine functions
# -----------------------------

def compute_discipline_score(tasks: List[Dict[str, Any]]) -> int:
    """Calculate a discipline score (0‑100).

    The score combines two ratios:
    * Completion ratio – proportion of tasks that are ``Done``.
    * Priority ratio – proportion of high‑priority tasks that are finished.

    Both ratios are weighted equally and scaled to 0‑100.
    """
    if not tasks:
        return 0

    total = len(tasks)
    done = sum(1 for t in tasks if t.get("status") == "Done")
    # High‑priority tasks (treat "High" only; others are medium/low)
    high_total = sum(1 for t in tasks if t.get("priority", "Medium").lower() == "high")
    high_done = sum(
        1
        for t in tasks
        if t.get("priority", "Medium").lower() == "high" and t.get("status") == "Done"
    )

    # Avoid division by zero
    completion_ratio = done / total
    priority_ratio = (high_done / high_total) if high_total else 1.0

    # Simple average, scaled to 0‑100
    score = int(((completion_ratio + priority_ratio) / 2) * 100)
    return score


def generate_schedule(tasks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Generate a strict, time‑blocked daily schedule.

    The implementation is deterministic and does **not** require an LLM key.
    It creates hourly blocks (9 AM – 5 PM) and assigns the pending
    ``To Do`` and ``In Progress`` tasks in order of priority (High → Medium → Low).
    If there are more tasks than slots, the excess tasks are listed under
    a "Backlog" slot.
    """
    # Filter pending tasks
    pending = [t for t in tasks if t.get("status") in {"To Do", "In Progress"}]

    # Sort by priority (High > Medium > Low) then by title alphabetically
    priority_order = {"high": 0, "medium": 1, "low": 2}
    pending.sort(
        key=lambda t: (
            priority_order.get(t.get("priority", "Medium").lower(), 1),
            t.get("title", "").lower(),
        )
    )

    schedule = []
    start_hour = 9
    end_hour = 17  # exclusive – 5 PM is the last start time
    slot = 0

    for task in pending:
        if start_hour + slot >= end_hour:
            # No more slots – put remaining tasks into a backlog entry
            break
        block_start = datetime.time(hour=start_hour + slot)
        block_end = datetime.time(hour=start_hour + slot + 1)
        schedule.append(
            {
                "time": f"{block_start.strftime('%I:%M %p')} – {block_end.strftime('%I:%M %p')}",
                "task": task.get("title", "Untitled"),
            }
        )
        slot += 1

    # If we ran out of time slots but still have tasks, add a backlog entry
    if len(pending) > slot:
        remaining = [t.get("title", "Untitled") for t in pending[slot:]]
        schedule.append({"time": "Backlog", "task": ", ".join(remaining)})

    return schedule


def bottleneck_warning(tasks: List[Dict[str, Any]]) -> str | None:
    """Return a warning string if too many tasks are *In Progress*.

    Threshold is configurable; for now we treat >3 as a bottleneck.
    """
    in_progress = sum(1 for t in tasks if t.get("status") == "In Progress")
    if in_progress > 3:
        return f"You have {in_progress} tasks in progress – consider focusing on fewer tasks."
    return None


# -----------------------------
# FastAPI endpoint
# -----------------------------
class InsightResponse(BaseModel):
    discipline_score: int
    bottleneck_warning: str | None = None
    recommended_schedule: List[Dict[str, str]]

@router.get("/ai/insights/", response_model=InsightResponse)
def get_ai_insights(db: sqlalchemy.orm.Session = Depends(get_db)):
    """Gather AI‑driven insights for the productivity dashboard.

    1. Pull all tasks from the SQLite database.
    2. Compute a *Discipline Score*.
    3. Detect a bottleneck if many tasks are simultaneously ``In Progress``.
    4. Produce a simple daily schedule.
    """
    # Load tasks as plain dictionaries for easier manipulation
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

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found in the database.")

    score = compute_discipline_score(tasks)
    warning = bottleneck_warning(tasks)
    schedule = generate_schedule(tasks)

    return InsightResponse(
        discipline_score=score,
        bottleneck_warning=warning,
        recommended_schedule=schedule,
    )
