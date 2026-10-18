
# AgentFlow — Multi-Agent Task Automation System

An AI-powered task automation platform that coordinates specialized AI agents to research, plan, analyze, and verify complex tasks, then generates structured reports through an interactive web dashboard.

## Features

- **Multi-Agent Orchestration:** Uses LangGraph to coordinate specialized agents.
- **AI-Powered Research:** Integrates Tavily for web research.
- **Specialized Agents:** Supports research, planning, analysis, and verification.
- **Live Progress Updates:** Streams workflow and agent status updates to the frontend.
- **Automated Reports:** Generates structured Markdown reports with research sources.
- **Task History:** Saves completed tasks locally and allows users to reopen previous reports.
- **History Management:** Delete individual tasks or clear all saved history.
- **Task Cancellation:** Request cancellation from the dashboard.
- **REST API:** Provides FastAPI endpoints for task execution and health checks.
- **Automated Tests:** Tests API health, input validation, and cancellation behavior.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| Agent Orchestration | LangGraph |
| Language Model | Groq API |
| Web Research | Tavily API |
| Report Rendering | React Markdown, remark-gfm |
| Testing | Pytest, HTTPX |
| Version Control | Git, GitHub |

## Architecture

1. The user submits a task through the React dashboard.
2. FastAPI receives the request and starts the workflow.
3. LangGraph coordinates the selected specialized agents.
4. Agents perform their assigned work, using web research when needed.
5. The workflow streams agent progress to the frontend.
6. A final report is generated and displayed as Markdown.
7. Completed tasks can be reopened from browser-based task history.

## Project Structure

```text
Multi-task agent/
├── app/
│   ├── api.py
│   └── graph_workflow.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
├── tests/
│   └── test_api.py
├── .env
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.10 or a compatible supported Python version
- Node.js and npm
- Groq API key
- Tavily API key

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/gouse0064-star/multi-agent-task-automation.git
cd multi-agent-task-automation
```

### 2. Set up the Python environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If `requirements.txt` is not present in the repository yet, create it with the project's actual Python dependencies before following this step.

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Replace the placeholders with your own API keys. Never commit `.env` or publish API keys.

### 4. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

## Running the Application

Open two terminals in the project root.

### Terminal 1 — Backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.api:app --reload
```

Backend: http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/api/health

### Terminal 2 — Frontend

```powershell
cd frontend
npm.cmd run dev
```

Frontend: http://localhost:5173

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status |
| GET | `/api/health` | Health check |
| POST | `/api/tasks` | Execute a task synchronously |
| POST | `/api/tasks/stream` | Execute a task with streaming progress |
| POST | `/api/tasks/{task_id}/cancel` | Request cancellation of an active task |

For streaming requests, send a JSON body containing the task and include the `X-Task-ID` header.

Example request body:

```json
{
  "task": "Research current AI agent trends and prepare a concise report."
}
```

## Running Tests

Run the automated API tests from the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_api.py -v
```

The current test suite covers health checks, basic API responses, task validation, and cancellation signaling without running real AI workflows.

## Current Limitations

- Task history is stored in browser `localStorage`, not a shared database.
- Cancellation is cooperative: an in-progress synchronous AI request may need to finish before the workflow can stop.
- The application requires valid API credentials and internet connectivity for AI and web-research features.
- Deployment and production authentication have not yet been documented as implemented features.

## Future Improvements

- Persistent task storage using SQLite or PostgreSQL.
- More comprehensive automated tests for workflow execution and streaming.
- Improved retry logic and rate-limit handling.
- User authentication and task ownership.
- Deployment and monitoring.
- More detailed workflow observability.

## Author

**MD GOUSE**

GitHub: https://github.com/gouse0064-star
