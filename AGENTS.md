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

## 4. Architectural Rules & Implementation Requirements
4.1. Security & Public Repository Hygiene
NEVER hardcode API keys, tokens, personal file paths, or sample personal resumes in the codebase.
All user-specific data (resumes, stop words, LLM API keys, scraped vacancies) must be stored exclusively in the local SQLite database (data/vacancies_search.db).
Browser session cookies and storage must reside exclusively in data/browser_profile/.
The data/ directory, .env, *.db, and *.sqlite* files must be ignored in .gitignore. On startup, the backend must automatically create the data/ directory if it does not exist.
4.2. Browser Automation (Playwright)
Use async_playwright with chromium.launch_persistent_context(user_data_dir="data/browser_profile", ...).
Manual Login Mode (POST /api/browser/open-login): Launches Chromium with headless=False pointing to a startup URL (or a user-provided URL) so the user can manually log into job boards. Once the user closes the window, cookies and session state persist locally.
Concurrency Control: Protect browser launch operations with a shared asyncio.Lock() so that background scraping tasks and manual login sessions never attempt to access data/browser_profile simultaneously (which causes Chromium profile lock crashes).
Human-like Pacing: Add randomized delays (await asyncio.sleep(random.uniform(1.5, 4.0))) between page navigations during scraping.
4.3. Universal Scraping & LLM Scoring Pipeline
Link Extraction from Search Pages: Because users can add arbitrary job board URLs, strip <script>, <style>, and <svg> tags from the rendered DOM, convert the main content into compact text/Markdown preserving href attributes, and use an LLM call to extract an array of individual vacancy URLs.
Deduplication: Before navigating to an individual vacancy URL, check the Vacancy table by url to skip already processed listings.
Vacancy Scoring: Pass the cleaned full vacancy text along with UserProfile data (resume, preferences, stop words) to the LLM using Structured Outputs / JSON Schema to enforce the following output:
match_score (int, 0–100)
pros (list[str] — reasons why the vacancy fits the candidate)
cons (list[str] — missing requirements or red flags)
is_stop_word_triggered (bool)
summary (str — concise 2-sentence overview of the role)
4.4. Database Models (backend/app/models.py)
UserProfile: id, resume_text, preferences, stop_words, min_match_score (default: 70), updated_at.
JobSource: id, name, url, is_active (bool), check_interval_hours (int, default: 4), last_run_at, last_status, last_error.
Vacancy: id, source_id, url (unique index), title, company, salary, raw_text, match_score, ai_summary, pros_json, cons_json, status (new | favorite | applied | rejected), created_at.
AppSettings: id, llm_api_key, llm_base_url (default: "https://api.openai.com/v1"), llm_model (default: "gpt-4o-mini").
## 5. Codex Workflow & Quality Standards
Code Style:
Python: Use strict type hints, follow PEP 8, and use async/await for all I/O operations (database, HTTP requests, Playwright).
TypeScript: Enable strict mode ("strict": true), avoid any.
Sandbox Testing:
The Codex execution environment does not have a graphical display server (X11/Wayland) or live internet access to job boards.
All unit and integration tests for scraper, browser, and llm modules must mock external dependencies (unittest.mock.AsyncMock).
Before finishing any task, always run pytest inside /backend and npm run build inside /frontend to verify there are no broken tests, type errors, or build failures.
API Synchronization:
Whenever backend endpoints or Pydantic schemas change, update the corresponding TypeScript interfaces in frontend/src/types/ and API client functions in frontend/src/api/.
All backend routes must be prefixed with /api/....
