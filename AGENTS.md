# AGENTS.md — Development Guidelines for `vacancies-search`

## 1. Project Overview
`vacancies-search` is a local full-stack web application designed to automate job search and AI-powered vacancy filtering without automated job applications.
The user manually logs into job boards (e.g., hh.ru, LinkedIn, Habr Career, etc.) via an integrated browser instance (Playwright Persistent Context), adds search result URLs, and configures their candidate profile. A background agent periodically scrapes new vacancies from these sources and evaluates their relevance using an LLM.

This repository is **public**. Application code must remain strictly separated from personal data, browser sessions, databases, and API keys.

---

## 2. Technology Stack
Strictly adhere to the following stack. Do not introduce heavy message brokers (Redis/Celery) or external database servers:

### Backend (`/backend`)
* **Language:** Python 3.11+
* **Web Framework:** FastAPI (async) + Uvicorn
* **Database:** SQLite + SQLModel (or SQLAlchemy 2.0 + Pydantic v2)
* **Browser & Scraping:** `playwright` (async API), `beautifulsoup4`, `trafilatura` (or `html2text` to convert HTML into clean Markdown before passing it to an LLM)
* **Task Scheduler:** `APScheduler` (`AsyncIOScheduler` running inside the FastAPI lifecycle)
* **LLM Integration:** Official `openai` Python SDK (supporting custom `base_url` for OpenAI-compatible providers and Structured Outputs / JSON mode)
* **Testing:** `pytest`, `pytest-asyncio`, `httpx`

### Frontend (`/frontend`)
* **Framework & Build Tool:** React 18+ (Vite + TypeScript)
* **Styling:** Tailwind CSS
* **Icons & UI:** `lucide-react` and clean, accessible components (in the style of `shadcn/ui`)
* **HTTP Client:** Typed `fetch` wrapper or `axios` matching backend Pydantic schemas

---

## 3. Repository Structure
```text
vacancies-search/
├── AGENTS.md                 # Architectural rules and instructions for Codex
├── README.md                 # Documentation and local setup instructions
├── .gitignore                # Exclusions protecting personal data, cookies, and keys
├── .env.example              # Environment variables template
├── start.sh                  # Local startup script (Linux/macOS)
├── start.bat                 # Local startup script (Windows)
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point, CORS, APScheduler initialization
│   │   ├── config.py         # Path configurations (SQLite DB, browser_profile) and env
│   │   ├── database.py       # SQLite engine and async session management
│   │   ├── models.py         # SQLModel database tables and Pydantic request/response schemas
│   │   ├── api/              # FastAPI routers (vacancies, sources, profile, browser, settings)
│   │   ├── browser/          # Playwright Persistent Context manager & lock
│   │   ├── scraper/          # Search page link extraction & full vacancy text scraping
│   │   └── llm/              # Prompts and LLM client for vacancy scoring
│   ├── tests/                # Unit and API tests (using mocks for Playwright and LLM)
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/              # Typed API client calls to FastAPI
    │   ├── components/       # Reusable UI components
    │   ├── pages/            # Views: Dashboard, Sources, ProfileAndSettings
    │   ├── types/            # TypeScript interfaces (strictly synced with models.py)
    │   └── App.tsx
    └── package.json
