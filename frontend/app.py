import streamlit as st
import requests

# ── Config ───────────────────────────────────────────────────────────────────
TASKS_API = "http://127.0.0.1:8000/tasks"
AI_API    = "http://127.0.0.1:8000/ai/insights/"

st.set_page_config(
    page_title="AI Productivity Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session-state initialisation ──────────────────────────────────────────────
# Store AI insights so they survive Kanban interactions without re-fetching
if "ai_insights"      not in st.session_state: st.session_state.ai_insights      = None
if "ai_error"         not in st.session_state: st.session_state.ai_error         = None
if "ai_loading_done"  not in st.session_state: st.session_state.ai_loading_done  = False

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #e2e8f0;
}

/* ── AI Hub banner ── */
.ai-hub-banner {
    background: linear-gradient(90deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
    border: 1px solid rgba(99,102,241,0.4);
    border-radius: 16px;
    padding: 24px 32px 20px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(99,102,241,0.15), inset 0 1px 0 rgba(255,255,255,0.05);
}
.ai-hub-banner::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at center, rgba(99,102,241,0.08) 0%, transparent 60%);
    animation: pulse-glow 4s ease-in-out infinite;
}
@keyframes pulse-glow {
    0%,100% { opacity:.5; } 50% { opacity:1; }
}
.ai-hub-title {
    font-size: 1.5rem; font-weight: 800;
    background: linear-gradient(90deg,#818cf8,#c084fc,#38bdf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -.02em; margin: 0 0 6px;
}
.ai-hub-subtitle { color:#94a3b8; font-size:.875rem; margin:0; }
.ai-hub-badge {
    display:inline-block;
    background:rgba(99,102,241,0.2); border:1px solid rgba(99,102,241,0.4);
    color:#a5b4fc; font-size:.7rem; font-weight:600;
    letter-spacing:.1em; padding:3px 10px; border-radius:20px;
    margin-bottom:12px; text-transform:uppercase;
}
.ai-hub-empty {
    margin-top:16px; padding:16px;
    background:rgba(15,20,40,0.6); border-radius:10px;
    border:1px dashed rgba(99,102,241,0.3);
    color:#64748b; font-size:.8rem; text-align:center; font-style:italic;
}

/* ── Metric card row ── */
.metric-row { display:flex; gap:20px; flex-wrap:wrap; margin:16px 0 4px; }
.metric-card {
    flex:1; min-width:160px;
    background:rgba(99,102,241,0.12); border:1px solid rgba(99,102,241,0.25);
    border-radius:12px; padding:16px 20px;
}
.metric-label { color:#94a3b8; font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; }
.metric-value { font-size:2.2rem; font-weight:800; color:#e0e7ff; line-height:1.1; }
.metric-delta { font-size:.78rem; margin-top:4px; }

/* ── Schedule list ── */
.schedule-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:8px 14px; border-bottom:1px solid rgba(255,255,255,0.06);
    font-size:.83rem;
}
.schedule-row:last-child { border-bottom:none; }
.schedule-time { color:#818cf8; font-weight:600; min-width:170px; }
.schedule-task { color:#e2e8f0; }

/* ── Kanban headers ── */
.kanban-header-todo {
    background:linear-gradient(135deg,#334155,#1e293b);
    border-top:3px solid #64748b; border-radius:12px 12px 0 0;
    padding:14px 18px; font-weight:700; font-size:.9rem;
    letter-spacing:.05em; text-transform:uppercase; color:#94a3b8;
}
.kanban-header-inprogress {
    background:linear-gradient(135deg,#1e3a5f,#172554);
    border-top:3px solid #3b82f6; border-radius:12px 12px 0 0;
    padding:14px 18px; font-weight:700; font-size:.9rem;
    letter-spacing:.05em; text-transform:uppercase; color:#60a5fa;
}
.kanban-header-done {
    background:linear-gradient(135deg,#14532d,#052e16);
    border-top:3px solid #22c55e; border-radius:12px 12px 0 0;
    padding:14px 18px; font-weight:700; font-size:.9rem;
    letter-spacing:.05em; text-transform:uppercase; color:#4ade80;
}

/* ── Task cards ── */
.task-card {
    background:rgba(30,41,59,0.8); backdrop-filter:blur(10px);
    border:1px solid rgba(255,255,255,0.07); border-radius:12px;
    padding:16px; margin-bottom:12px;
    transition:all .2s ease; box-shadow:0 4px 6px rgba(0,0,0,0.3);
}
.task-card:hover {
    border-color:rgba(99,102,241,0.4);
    box-shadow:0 8px 20px rgba(0,0,0,0.4), 0 0 0 1px rgba(99,102,241,0.2);
    transform:translateY(-1px);
}
.task-title  { font-size:.95rem; font-weight:600; color:#e2e8f0; margin:0 0 6px; }
.task-desc   { font-size:.78rem; color:#94a3b8; margin:0 0 10px; line-height:1.5; }
.priority-badge { display:inline-block; font-size:.65rem; font-weight:700;
    letter-spacing:.08em; text-transform:uppercase; padding:2px 8px;
    border-radius:20px; margin-bottom:10px; }
.priority-high   { background:rgba(239,68,68,0.2);   color:#f87171; border:1px solid rgba(239,68,68,0.3); }
.priority-medium { background:rgba(245,158,11,0.2);  color:#fbbf24; border:1px solid rgba(245,158,11,0.3); }
.priority-low    { background:rgba(34,197,94,0.2);   color:#4ade80; border:1px solid rgba(34,197,94,0.3); }
.empty-col {
    background:rgba(15,20,40,0.4); border:1px dashed rgba(255,255,255,0.08);
    border-radius:0 0 12px 12px; padding:32px 16px;
    text-align:center; color:#475569; font-size:.8rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#0f1729 0%,#0d1117 100%);
    border-right:1px solid rgba(99,102,241,0.15);
}

/* Labels and Headers in Sidebar */
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Inputs, TextAreas, and Selectboxes */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea,
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background-color: #1E293B !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    color: #FFFFFF !important; 
    border-radius: 8px !important;
}

/* Placeholders */
[data-testid="stSidebar"] .stTextInput input::placeholder,
[data-testid="stSidebar"] .stTextArea textarea::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}

/* Selectbox Dropdown Menu (applies globally) */
ul[data-baseweb="menu"] {
    background-color: #1E293B !important;
}
ul[data-baseweb="menu"] li {
    color: #FFFFFF !important;
    background-color: transparent !important;
}
ul[data-baseweb="menu"] li:hover {
    background-color: #2563EB !important;
}

.stat-pill {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.2);
    border-radius:20px; padding:4px 12px; font-size:.78rem;
    color:#a5b4fc; font-weight:500;
}

/* ── Buttons ── */
/* Base button styles (used for secondary/delete actions) */
.stButton button {
    border-radius:8px !important; 
    font-size:.75rem !important;
    font-weight:600 !important; 
    padding:4px 12px !important;
    transition:all .15s ease !important;
    background-color: transparent !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}
.stButton button:hover { 
    transform:scale(1.03); 
    border-color: #FFFFFF !important;
    color: #FFFFFF !important;
}

/* Primary buttons (e.g. "Generate AI Schedule" and "Create Task") */
button[data-testid="baseButton-primary"] {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 6px rgba(37,99,235,0.3) !important;
}
button[data-testid="baseButton-primary"]:hover {
    background-color: #1D4ED8 !important;
}

hr { border-color:rgba(99,102,241,0.15) !important; }
</style>
""", unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────────────────────────

def fetch_tasks() -> list:
    try:
        r = requests.get(f"{TASKS_API}/", timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Could not reach backend: {e}")
        return []


def create_task(title: str, description: str, priority: str) -> bool:
    try:
        r = requests.post(f"{TASKS_API}/",
                          json={"title": title, "description": description,
                                "priority": priority, "status": "To Do"},
                          timeout=10)
        r.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create task: {e}")
        return False


def update_task_status(task_id: int, new_status: str) -> bool:
    try:
        r = requests.put(f"{TASKS_API}/{task_id}",
                         json={"status": new_status}, timeout=10)
        r.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to update task: {e}")
        return False


def delete_task(task_id: int) -> bool:
    try:
        r = requests.delete(f"{TASKS_API}/{task_id}", timeout=10)
        r.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to delete task: {e}")
        return False


def fetch_ai_insights() -> dict | None:
    try:
        r = requests.get(AI_API, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API Error: {str(e)}")


def priority_badge_html(priority: str) -> str:
    p = (priority or "Medium").lower()
    cls  = "priority-high" if p == "high" else "priority-medium" if p == "medium" else "priority-low"
    icon = "🔴" if p == "high" else "🟡" if p == "medium" else "🟢"
    return f'<span class="priority-badge {cls}">{icon} {priority or "Medium"}</span>'


def score_color(score: int) -> str:
    if score >= 70: return "#4ade80"
    if score >= 40: return "#fbbf24"
    return "#f87171"


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding:8px 0 20px;'>
        <div style='font-size:1.4rem;font-weight:800;
                    background:linear-gradient(90deg,#818cf8,#c084fc);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;'>⚡ Task Manager</div>
        <div style='color:#64748b;font-size:.78rem;margin-top:4px;'>AI Productivity Dashboard</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("### ＋ Add New Task")
    with st.form("add_task_form", clear_on_submit=True):
        title       = st.text_input("Task Title", placeholder="e.g. Design landing page")
        description = st.text_area("Description", placeholder="Brief description…", height=100)
        priority    = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
        submitted   = st.form_submit_button("🚀 Create Task", use_container_width=True)

    if submitted:
        if title.strip():
            if create_task(title.strip(), description.strip(), priority):
                st.success("Task created!", icon="✅")
                st.rerun()
        else:
            st.warning("Please enter a task title.")

    st.divider()

    # Live stats
    all_tasks   = fetch_tasks()
    todo_count  = sum(1 for t in all_tasks if t.get("status") == "To Do")
    prog_count  = sum(1 for t in all_tasks if t.get("status") == "In Progress")
    done_count  = sum(1 for t in all_tasks if t.get("status") == "Done")

    st.markdown("### 📊 Overview")
    st.markdown(f"""
    <div style='display:flex;flex-direction:column;gap:8px;margin-top:8px;'>
        <div class='stat-pill'>📋 To Do &nbsp;<strong>{todo_count}</strong></div>
        <div class='stat-pill'>⚙️ In Progress &nbsp;<strong>{prog_count}</strong></div>
        <div class='stat-pill'>✅ Done &nbsp;<strong>{done_count}</strong></div>
        <div class='stat-pill'>🗂️ Total &nbsp;<strong>{len(all_tasks)}</strong></div>
    </div>""", unsafe_allow_html=True)

    st.divider()
    # Clear cached insights from sidebar
    if st.button("🔄 Clear AI Insights", use_container_width=True):
        st.session_state.ai_insights     = None
        st.session_state.ai_error        = None
        st.session_state.ai_loading_done = False
        st.rerun()


# ── AI Discipline Hub ─────────────────────────────────────────────────────────

insights = st.session_state.ai_insights

# Banner wrapper (always shown)
st.markdown("""
<div class="ai-hub-banner">
    <div class="ai-hub-badge">✦ Powered by AI</div>
    <div class="ai-hub-title">🧠 AI Discipline Hub</div>
    <p class="ai-hub-subtitle">
        Real-time algorithmic coaching, workflow balance, and time-blocking.
    </p>
</div>""", unsafe_allow_html=True)

# ── Generate button + results ─────────────────────────────────────────────────
hub_col, _ = st.columns([2, 1])

with hub_col:
    if st.button("✨ Generate AI Schedule & Insights",
                 use_container_width=True,
                 type="primary",
                 key="gen_ai_btn"):
        with st.spinner("🤖 Gemini is analyzing your workflow…"):
            try:
                data = fetch_ai_insights()
                st.session_state.ai_insights     = data
                st.session_state.ai_error        = None
                st.session_state.ai_loading_done = True
            except Exception as e:
                st.session_state.ai_error        = str(e)
                st.session_state.ai_loading_done = True

# Show error if any
if st.session_state.ai_error:
    st.error(f"⚠️ Could not fetch AI insights: {st.session_state.ai_error}", icon="🚨")

# Show results if we have them
if insights:
    score    = insights.get("discipline_score", 0)
    warning  = insights.get("bottleneck_warning")
    schedule = insights.get("recommended_schedule", [])

    # ── Discipline score metric ───────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)

    with m1:
        color = score_color(score)
        label = "🔥 On fire!" if score >= 70 else "⚡ Keep going!" if score >= 40 else "😓 Needs focus"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Discipline Score</div>
            <div class="metric-value" style="color:{color};">{score}<span style="font-size:1rem;color:#64748b;">/100</span></div>
            <div class="metric-delta" style="color:{color};">{label}</div>
        </div>""", unsafe_allow_html=True)

    with m2:
        in_prog = sum(1 for t in all_tasks if t.get("status") == "In Progress")
        ip_color = "#f87171" if in_prog > 3 else "#4ade80"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">In Progress</div>
            <div class="metric-value" style="color:{ip_color};">{in_prog}</div>
            <div class="metric-delta" style="color:{ip_color};">
                {"⚠️ Too many!" if in_prog > 3 else "✅ Healthy WIP"}
            </div>
        </div>""", unsafe_allow_html=True)

    with m3:
        total  = len(all_tasks)
        done_n = sum(1 for t in all_tasks if t.get("status") == "Done")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tasks Completed</div>
            <div class="metric-value" style="color:#818cf8;">{done_n}<span style="font-size:1rem;color:#64748b;">/{total}</span></div>
            <div class="metric-delta" style="color:#94a3b8;">{"No tasks yet" if total == 0 else f"{int(done_n/total*100)}% done"}</div>
        </div>""", unsafe_allow_html=True)

    # ── Bottleneck warning ────────────────────────────────────────────────────
    if warning:
        st.warning(f"🚦 **Bottleneck Detected** — {warning}", icon="⚠️")

    # ── Recommended schedule ──────────────────────────────────────────────────
    if schedule:
        with st.expander("📅 Your AI-Optimized Daily Schedule", expanded=True):
            st.markdown(
                "<div style='background:rgba(15,20,40,0.6);border-radius:10px;"
                "border:1px solid rgba(99,102,241,0.2);overflow:hidden;margin-top:8px;'>",
                unsafe_allow_html=True,
            )
            for i, item in enumerate(schedule):
                bg = "rgba(99,102,241,0.06)" if i % 2 == 0 else "transparent"
                time_label = item.get("time", "—")
                task_label = item.get("task", "—")
                is_backlog = time_label.lower() == "backlog"
                time_color = "#f59e0b" if is_backlog else "#818cf8"
                st.markdown(f"""
                <div class="schedule-row" style="background:{bg};">
                    <span class="schedule-time" style="color:{time_color};">
                        {"📦" if is_backlog else "⏰"} {time_label}
                    </span>
                    <span class="schedule-task">• {task_label}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("🎉 No pending tasks to schedule — all caught up!", icon="✅")

elif not st.session_state.ai_loading_done:
    # First-visit placeholder
    st.markdown("""
    <div class="ai-hub-empty">
        💡 Click <strong>Generate AI Schedule &amp; Insights</strong> above to analyze your workflow.
    </div>""", unsafe_allow_html=True)

st.markdown("---")


# ── Kanban Board ──────────────────────────────────────────────────────────────

st.markdown("## 📌 Kanban Board")

tasks      = fetch_tasks()
todo_tasks = [t for t in tasks if t.get("status") == "To Do"]
inprog_tasks = [t for t in tasks if t.get("status") == "In Progress"]
done_tasks = [t for t in tasks if t.get("status") == "Done"]

col_todo, col_prog, col_done = st.columns(3)


def render_task_card(task: dict, col) -> None:
    with col:
        with st.container():
            st.markdown(f"""
            <div class="task-card">
                <div class="task-title">📝 {task.get('title','Untitled')}</div>
                <div class="task-desc">{task.get('description') or '<em>No description</em>'}</div>
                {priority_badge_html(task.get('priority','Medium'))}
            </div>""", unsafe_allow_html=True)

            btn_cols = st.columns([1, 1, 1])
            status   = task.get("status", "To Do")
            tid      = task["id"]

            if status == "To Do":
                if btn_cols[0].button("▶ Start", key=f"start_{tid}", use_container_width=True):
                    if update_task_status(tid, "In Progress"):
                        st.rerun()
            elif status == "In Progress":
                if btn_cols[0].button("✔ Complete", key=f"done_{tid}", use_container_width=True):
                    if update_task_status(tid, "Done"):
                        st.rerun()
                if btn_cols[1].button("↩ Revert", key=f"revert_{tid}", use_container_width=True):
                    if update_task_status(tid, "To Do"):
                        st.rerun()
            elif status == "Done":
                if btn_cols[0].button("↩ Reopen", key=f"reopen_{tid}", use_container_width=True):
                    if update_task_status(tid, "To Do"):
                        st.rerun()

            if btn_cols[2].button("🗑", key=f"del_{tid}", use_container_width=True, help="Delete task"):
                if delete_task(tid):
                    st.rerun()

            st.markdown("<hr style='margin:6px 0;border-color:rgba(255,255,255,0.05);'>",
                        unsafe_allow_html=True)


# ── To Do ─────────────────────────────────────────────────────────────────────
with col_todo:
    st.markdown(
        f'<div class="kanban-header-todo">📋 To Do '
        f'<span style="margin-left:auto;font-size:.75rem;background:rgba(100,116,139,0.3);'
        f'padding:2px 8px;border-radius:20px;">{len(todo_tasks)}</span></div>',
        unsafe_allow_html=True)
    if not todo_tasks:
        st.markdown('<div class="empty-col">No tasks here yet.</div>', unsafe_allow_html=True)
    for task in todo_tasks:
        render_task_card(task, col_todo)

# ── In Progress ───────────────────────────────────────────────────────────────
with col_prog:
    st.markdown(
        f'<div class="kanban-header-inprogress">⚙️ In Progress '
        f'<span style="margin-left:auto;font-size:.75rem;background:rgba(59,130,246,0.3);'
        f'padding:2px 8px;border-radius:20px;">{len(inprog_tasks)}</span></div>',
        unsafe_allow_html=True)
    if not inprog_tasks:
        st.markdown('<div class="empty-col">No tasks in progress.</div>', unsafe_allow_html=True)
    for task in inprog_tasks:
        render_task_card(task, col_prog)

# ── Done ──────────────────────────────────────────────────────────────────────
with col_done:
    st.markdown(
        f'<div class="kanban-header-done">✅ Done '
        f'<span style="margin-left:auto;font-size:.75rem;background:rgba(34,197,94,0.3);'
        f'padding:2px 8px;border-radius:20px;">{len(done_tasks)}</span></div>',
        unsafe_allow_html=True)
    if not done_tasks:
        st.markdown('<div class="empty-col">No completed tasks yet.</div>', unsafe_allow_html=True)
    for task in done_tasks:
        render_task_card(task, col_done)
