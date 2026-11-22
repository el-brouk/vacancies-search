# vacancies-search

Local full-stack application for finding and evaluating relevant vacancies.

## Backend setup

The backend requires Python 3.11 or newer. From the repository root:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
cp .env.example .env
backend/.venv/bin/uvicorn app.main:app --app-dir backend --reload
```

The API is available at `http://127.0.0.1:8000`; its health endpoint is
`/api/health` and the OpenAPI page is `/docs`. On startup, the backend creates
the local `data/` directory, initializes the SQLite schema in
`data/vacancies_search.db`, and starts the in-process scheduler. Configure
optional settings with the `VACANCIES_` environment variable prefix or `.env`.
Personal data, database files, and browser state belong in `data/` and are
excluded from Git.
automatisation of searching for relevant vacancies
