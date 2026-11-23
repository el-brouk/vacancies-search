# Project Plan

Build `vacancies-search` as a local application that collects vacancies and helps the user evaluate them with an LLM. Job applications remain manual. Complete the tasks in order; each task assumes the tasks above it are complete.

1. [x] Add `.gitignore` rules for local data, browser profiles, `.env`, databases, virtual environments, dependencies, and build output.
2. [x] Add `.env.example` with non-secret configuration names and safe defaults.
3. [x] Set up the backend and frontend project structure, dependency manifests, and supported runtime versions.
4. [ ] Add local startup scripts and document setup and startup in `README.md`.
5. [ ] Implement typed backend configuration and paths for SQLite and the browser profile; create the local `data/` directory on startup.
6. [ ] Configure async SQLite access and database initialization.
7. [ ] Define profile, source, vacancy, and settings models and request/response schemas, including required constraints, indexes, and safe API-key handling.
8. [ ] Create the FastAPI lifecycle and `/api/` router structure; configure local frontend CORS and consistent validation/error responses.
9. [ ] Implement source CRUD, profile/settings, vacancy listing/detail, and vacancy status API endpoints.
10. [ ] Set up React, Vite, TypeScript strict mode, Tailwind CSS, and the shared UI components needed for the first workflow.
11. [ ] Define frontend types to match backend schemas and add a typed API client for the endpoints from step 9.
12. [ ] Build basic source, profile/settings, and vacancy views against the API; include loading, empty, validation, and error states.
13. [ ] Check keyboard access, labels, focus behavior, and responsive layouts in those views.
14. [ ] Implement Playwright persistent-context access using `data/browser_profile/` and a shared async lock for every use of the browser profile.
15. [ ] Add a manual login action that opens Chromium at a supplied or default URL and reports browser availability and startup errors.
16. [ ] Add a manual “run source now” API action and report run status, timestamps, and actionable errors.
17. [ ] Choose the first target job board or a simple link-extraction approach for its search pages.
18. [ ] Extract vacancy links from rendered search pages, skip URLs already in the database, and scrape and clean vacancy descriptions.
19. [ ] Add randomized pacing between page navigations.
20. [ ] Implement the OpenAI-compatible LLM client with configurable base URL and model.
21. [ ] Score vacancies using structured output: score, pros, cons, stop-word flag, and concise summary; store results in SQLite.
22. [ ] Connect the manual collection action to the UI and show score, summary, pros, cons, and controls to change vacancy status.
23. [ ] Run APScheduler within the FastAPI lifecycle and schedule active sources according to their check interval.
24. [ ] Ensure scheduled runs use the shared browser-profile lock and report failures without hiding their causes.
25. [ ] Add focused backend tests for API workflows, scraping, browser locking, scheduler behavior, and LLM output handling; mock Playwright and LLM calls.
26. [ ] Run `pytest` from `backend/` and `npm run build` from `frontend/`; fix any failures before acceptance.
27. [ ] Complete a clean-checkout acceptance run: configure profile and LLM, log in, collect and score vacancies, verify duplicate skipping, change a vacancy status, and confirm scheduled run status.
28. [ ] Confirm no personal data, browser state, database, or secret is tracked in the public repository; finish setup and troubleshooting documentation.
