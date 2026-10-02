# Backward compatibility proxy: forwards execution to frontend/app.py
from pathlib import Path

_frontend_script = Path(__file__).resolve().parent / "frontend" / "app.py"
with open(_frontend_script, encoding="utf-8") as _f:
    code = compile(_f.read(), str(_frontend_script), "exec")
    exec(code, globals())
