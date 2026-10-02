🧠 AI-Powered Kanban Dashboard

An intelligent, modular productivity dashboard that combines a traditional Kanban workflow with Google Gemini AI. Instead of just tracking tasks, this application acts as an AI productivity coach—analyzing your pending work, calculating a "Discipline Score," detecting workflow bottlenecks, and automatically generating an optimized, time-blocked daily schedule.

✨ Key Features

Interactive Kanban Board: Clean, dark-mode UI with drag-and-drop style functionality to move tasks between "To Do", "In Progress", and "Done".

AI Discipline Hub: Real-time AI analysis of your current workload.

Smart Scheduling: Generates a time-blocked schedule based on task priorities and current status.

Bottleneck Detection: Identifies if too many tasks are stuck "In Progress" and provides actionable warnings.

Modular Architecture: Strictly separated FastAPI backend and Streamlit frontend for scalability and clean code management.

🛠️ Tech Stack

Frontend: Streamlit, Custom CSS

Backend: FastAPI, Python

Database: SQLite, SQLAlchemy (ORM)

AI Integration: Google GenAI SDK (Gemini API)

Data Validation: Pydantic

📂 Project Structure

workspace/
├── backend/
│   ├── __init__.py
│   ├── database.py          # SQLite setup and session management
│   ├── models.py            # SQLAlchemy models & Pydantic schemas
│   ├── main.py              # FastAPI app initialization & CORS
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── tasks.py         # CRUD API endpoints for tasks
│   │   └── ai.py            # API endpoint for AI insights
│   └── services/
│       ├── __init__.py
│       └── ai_engine.py     # Google Gemini prompt logic & fallback scoring
├── frontend/
│   └── app.py               # Streamlit UI, styling, and API integration
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variable template
└── README.md


🚀 Installation & Setup

1. Clone the repository

git clone https://github.com/your-username/ai-kanban-dashboard.git
cd ai-kanban-dashboard


2. Set up the virtual environment

python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate


3. Install dependencies

pip install -r requirements.txt


4. Configure Environment Variables

Create a .env file in the root directory and add your Google Gemini API Key:

GEMINI_API_KEY=your_gemini_api_key_here


5. Run the Application

You will need to run the backend and frontend simultaneously in two separate terminal windows. Ensure both terminals are in the root workspace directory and the virtual environment is activated.

Terminal 1 (Backend - FastAPI):

python -m uvicorn backend.main:app --reload


The backend API will run at http://127.0.0.1:8000
View interactive API docs at http://127.0.0.1:8000/docs

Terminal 2 (Frontend - Streamlit):

python -m streamlit run frontend/app.py


The UI will open in your browser at http://localhost:8501

💡 How to Use

Add Tasks: Use the left sidebar to add new tasks with a Title, Description, and Priority (High, Medium, Low).

Manage Workflow: Click the action buttons on task cards to advance them from "To Do" ➡️ "In Progress" ➡️ "Done".

Get AI Insights: Click the Generate AI Schedule & Insights button at the top of the dashboard. Gemini will analyze your current board and provide a dynamic discipline score and a suggested daily schedule to tackle the remaining items.

🤝 Contributing

Contributions are welcome! If you'd like to improve the UI, add user authentication, or swap out the AI models, feel free to fork the repository and submit a pull request.

📜 License

This project is open-source and available under the MIT License.
