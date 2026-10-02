import os
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any

# ── Load .env / config.env from the project root ─────────────────────────────
try:
    from dotenv import load_dotenv
    _root = Path(__file__).resolve().parent.parent.parent  # workspace/
    # Try config.env first (in case .env is a directory), then .env
    _loaded = False
    for _env_file in ("config.env", ".env"):
        _path = _root / _env_file
        if _path.is_file():
            load_dotenv(dotenv_path=_path, override=False)
            _loaded = True
            break
    if not _loaded:
        load_dotenv(override=False)  # default fallback (searches CWD upward)
except ImportError:
    pass  # python-dotenv not installed; rely on shell env vars

try:
    from google import genai as google_genai
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False


def analyze_tasks(tasks: List[Dict[str, Any]]) -> dict:
    """Analyze tasks using Gemini (if API key available) or fallback to algorithmic scoring."""

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and _HAS_GENAI:
        try:
            client = google_genai.Client(api_key=api_key)

            prompt = f"""
Analyze the following list of tasks and return a JSON object with exactly these three keys:
- "discipline_score": integer 0-100 based on completion ratio and priority handling.
- "bottleneck_warning": string warning if >3 tasks are "In Progress", else null.
- "recommended_schedule": list of objects each with "time" (e.g. "09:00 AM - 10:00 AM") and "task" (title).
  Schedule high-priority "To Do" and "In Progress" items first, covering 9 AM to 5 PM only.

Tasks: {json.dumps(tasks)}

Return ONLY valid JSON. No markdown code fences, no extra text.
"""
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )

            text = response.text.strip()
            
            # Robust JSON extraction using regex
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                extracted_json = json_match.group(0)
            else:
                extracted_json = text

            return json.loads(extracted_json)

        except (json.JSONDecodeError, Exception) as e:
            print(f"Gemini API failed: {e}. Falling back to algorithmic scoring.")
            # fall through to algorithmic fallback


    # Algorithmic fallback
    if not tasks:
        return {
            "discipline_score": 100,
            "bottleneck_warning": None,
            "recommended_schedule": []
        }

    total = len(tasks)
    done = sum(1 for t in tasks if t.get("status") == "Done")
    discipline_score = int((done / total) * 100)

    in_progress = sum(1 for t in tasks if t.get("status") == "In Progress")
    bottleneck_warning = None
    if in_progress > 3:
        bottleneck_warning = f"Warning: {in_progress} tasks are 'In Progress' concurrently."

    pending = [t for t in tasks if t.get("status") in {"To Do", "In Progress"}]
    priority_order = {"high": 0, "medium": 1, "low": 2}
    pending.sort(
        key=lambda t: (
            priority_order.get(str(t.get("priority", "Medium")).lower(), 1),
            str(t.get("title", "")).lower(),
        )
    )

    schedule = []
    start_hour = 9
    end_hour = 17
    slot = 0

    for task in pending:
        if start_hour + slot >= end_hour:
            break
        block_start = datetime.time(hour=start_hour + slot)
        block_end = datetime.time(hour=start_hour + slot + 1)
        schedule.append(
            {
                "time": f"{block_start.strftime('%I:%M %p')} – {block_end.strftime('%I:%M %p')}",
                "task": task.get("title", "Untitled Task"),
            }
        )
        slot += 1

    return {
        "discipline_score": discipline_score,
        "bottleneck_warning": bottleneck_warning,
        "recommended_schedule": schedule
    }
