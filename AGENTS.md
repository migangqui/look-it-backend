# Repository Guidelines

This document explains how to contribute safely and predictably to the Look-It backend. Keep changes inside the `look-it-backend` folder and follow the conventions below so reviewers can focus on logic instead of process.

## Project Structure & Module Organization

- `app/` holds the FastAPI entry point (`app/main.py`), configuration (`settings.py`), routers under `app/api/v1`, and reusable services in `app/core`. Drop new business logic into the appropriate service module and expose it through a router.
- `app/db/mongo_models.py` defines the MongoDB schemas used by services.
- Top-level files such as `requirements.txt`, `pytest.ini`, and the two `Dockerfile` variants control dependencies, tests, and container builds.
- `tests/` mirrors the patterns in `app/`; keep any new fixtures or helpers close to the feature they cover (e.g., `tests/test_image_processor.py` for image-related work).

## Build, Test, and Development Commands

1. `python3 -m venv venv && source venv/bin/activate` – create and activate a virtual environment before installing packages.
2. `pip install -r requirements.txt` – install the declared dependencies.
3. `uvicorn app.main:app --reload` – start the development FastAPI server with autoreload.
4. `pytest` – run the full test suite (configured in `pytest.ini`).
5. `pytest --cov=app --cov-report=html` – execute tests with coverage reporting to `htmlcov/`.
6. `docker build -f Dockerfile -t look-it-backend .` – build the production image, or swap in `Dockerfile_LOCAL` for local experiments.

## Coding Style & Naming Conventions

- Follow PEP 8: four-space indentation, `snake_case` for functions/variables, and expressive names that hint at intent (e.g., `garment_service.py`, `auth_router.py`).
- Keep router files focused on request/response wiring; business logic belongs in the service layer under `app/core`.
- Test files follow the `test_*.py` naming pattern, classes start with `Test`, and test functions begin with `test_`. This aligns with the `pytest.ini` selectors.

## Testing Guidelines

- The suite relies on `pytest` and the coverage plugin defined in `requirements.txt`.
- Run targeted tests with `pytest tests/test_image_processor.py` or `pytest tests/test_image_processor.py::TestProcessImage::test_process_image_success`.
- Use `pytest -v` for verbose output when debugging.
- Add new tests next to the code they exercise and keep assertions deterministic; mock external services (e.g., Google Vision) with fixtures.

## Commit & Pull Request Guidelines

- Prefer conventional-style commit prefixes (`feat:`, `fix:`, `docs:`) as seen in recent history; keep each message short but descriptive.
- Every pull request should summarize the change, note which commands were run (especially `pytest`), and mention the related issue or ticket.
- Include screenshots/log snippets only when UI/API responses changed; describe how reviewers can verify the work locally.

## Security & Configuration Tips

- Store secrets outside the repo (e.g., `GOOGLE_CREDENTIALS`, `GCP_PROJECT_ID`) and avoid committing `.env` files.
- Use Google Secret Manager and Azure credentials sparingly; document required environment variables in `README.md` or `DEPLOYMENT.md`.
