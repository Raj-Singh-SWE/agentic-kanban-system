# AI-Powered Kanban System ⚡🧠

An intelligent, modular productivity dashboard that pairs a fast, lightweight backend with a sleek, dynamic Kanban board frontend. This application integrates Google's Gemini AI to analyze your workflow, warn you about bottlenecks, and dynamically generate an optimized daily schedule based on task priorities.

---

## 🏗️ Architecture

The system is decoupled into two primary components communicating over REST:

### 1. Backend (FastAPI + SQLite)
A highly performant, ASGI-compliant RESTful API built with **FastAPI**.
- **Database (`backend/database.py`)**: Uses SQLAlchemy with SQLite (configured with WAL mode for concurrent writes and anti-locking resiliency).
- **Models (`backend/models.py`)**: Pydantic schemas for data validation and SQLAlchemy ORM models.
- **Task Router (`backend/routers/tasks.py`)**: Standard CRUD endpoints to manage Kanban tasks.
- **AI Router & Engine (`backend/routers/ai.py` & `backend/services/ai_engine.py`)**: 
  - Retrieves active tasks and sends them to the **Gemini 3.8 Flash** model via the `google-genai` SDK.
  - Generates a JSON payload containing a `discipline_score`, `bottleneck_warning`, and an optimized `recommended_schedule`.
  - **Fail-safe mechanism**: Incorporates regex JSON extraction and algorithmic fallback logic (calculates scores and schedules manually) in case the LLM API is rate-limited or fails.

### 2. Frontend (Streamlit)
A highly customized, reactive UI built in **Streamlit** (`frontend/app.py`).
- **Custom CSS Design System**: Features a dark mode, glassmorphism UI, gradient text, and micro-animations to deliver a premium user experience.
- **State Management**: Persists AI insights in `st.session_state` to prevent unnecessary and expensive re-fetching when interacting with the Kanban board.
- **Error Handling**: Graceful fallback and API resiliency. If the backend drops, Streamlit cleanly surfaces the error without clearing state or infinite looping.

---

## 🛠️ Technology Stack

- **Frontend**: Streamlit, HTML/CSS (Vanilla injects)
- **Backend**: FastAPI, Uvicorn
- **Database**: SQLite, SQLAlchemy
- **AI Integration**: Google Gemini SDK (`google-genai`)
- **Environment**: `python-dotenv`
- **Docker**: Included for backend deployment
- **Streamlit Community Cloud**: Ready for `.streamlit/config.toml` deployment

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Raj-Singh-SWE/agentic-kanban-system.git
cd agentic-kanban-system
```

### 2. Create a virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a file named `config.env` (or `.env`) in the root directory of the project and add your Gemini API Key:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 4. Run the Backend
In a new terminal window, start the FastAPI server:
```bash
uvicorn backend.main:app --reload --port 8000
```
*API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

### 5. Run the Frontend
In another terminal window, start the Streamlit application:
```bash
streamlit run frontend/app.py
```
*The dashboard will open automatically in your browser at [http://localhost:8501](http://localhost:8501)*

---

## 💡 Usage Features
- **Create Tasks**: Quickly add tasks with titles, descriptions, and High/Medium/Low priority via the sidebar.
- **Kanban Flow**: Move tasks between `To Do`, `In Progress`, and `Done` using intuitive card buttons.
- **AI Discipline Hub**: Click "Generate AI Schedule & Insights" to let Gemini act as your staff productivity coach. It will balance your schedule between 9 AM and 5 PM and warn you if you have too much work in progress.
