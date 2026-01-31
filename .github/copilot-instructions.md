# Copilot instructions — Tophold 🧭

Purpose: give AI coding agents the minimal, actionable knowledge to be immediately productive in this repository.

## Quick context
- Flask web app packaged under `testapp` with top-level `server.py` that does `from testapp import app` and runs on port 5000.
- Templates are under `testapp/templates/testapp/`; static assets live in `static/` and the app sets `static_folder='../static'` in `testapp/__init__.py`.
- `requirements.txt` pins: Flask, Flask-SQLAlchemy, PyMySQL, python-dotenv, Pillow, qrcode, openpyxl, gunicorn — expect features around DB, images, QR codes and Excel.

## Key files & places to inspect 🔎
- `testapp/__init__.py` — Flask app creation and config loading.
- `testapp/config.py` — SECRET_KEY is currently hardcoded (`SECRET_KEY = 'secret'`) and contains commented example for using env-based config. Agents should prefer existing `.env` pattern (python-dotenv is installed) if adding secrets.
- `testapp/views.py` — route handlers. Note: there are incomplete/fragile spots (see Gotchas).
- `testapp/models/` — SQLAlchemy models (e.g., `employee.py`) expect a `db` object.
- `server.py` — simple app runner. Deployment may use `gunicorn server:app` or the systemd service `cd2025.service` (see file for example ExecStart path).

## Important patterns & gotchas ⚠️
- Mixed DB approaches: views call `get_db()` and run raw SQL, while models import `db` and assume Flask-SQLAlchemy. There is *no* `db = SQLAlchemy(app)` in `testapp/__init__.py` at present — treat DB work as incomplete and verify where to add initialization.
- Missing imports / incomplete auth flow in `testapp/views.py`: references to `flash`, `session`, and `check_password_hash` are used but not imported. Before changing logic, run the app to reproduce and fix import/runtime errors.
- Templates are referenced with the package path (e.g., `render_template('testapp/mainpage.html')`); maintain that structure when moving/adding templates.
- Secret management: `config.py` shows commented env pattern. Do not commit secrets; use `.env` / environment variables and `python-dotenv` for local dev.
- Deployment hint: `cd2025.service` shows a systemd pattern using a virtualenv and `server.py` ExecStart — for production use `gunicorn server:app` or follow the systemd file.
- Code contains Japanese comments and messages — preserve these when editing localized strings.

## Local dev & debugging commands ✅
- Setup: `python -m venv .venv && .\.venv\Scripts\Activate.ps1` (Windows) then `pip install -r requirements.txt`.
- Run dev server: `python server.py` → open `http://localhost:5000/`.
- Try `gunicorn server:app -w 4 -b 0.0.0.0:8000` for production-style runs (requires gunicorn on the target OS).
- If adding DB: set `SQLALCHEMY_DATABASE_URI` via env var; python-dotenv is available for local `.env` loading.

## Suggested cautious workflows for agents ✋
- Reproduce runtime errors locally first (run `python server.py`) and add minimal fixes (imports, missing variables) in small PRs.
- For DB changes: add `db = SQLAlchemy()` to `testapp/__init__.py` *and* initialize it after app creation (or use app factory pattern). Also add/verify `SQLALCHEMY_DATABASE_URI` in `testapp/config.py` or via env.
- When touching auth: prefer adding explicit imports (e.g., `from flask import flash, session`) and test the login flow manually — there are no automated tests in the repo to verify behavior.

## Examples (what to look for)
- Templates: `testapp/templates/testapp/mainpage.html` uses `{{ url_for('static', filename='css/style.css') }}` — static path is expected at `/static/css/style.css`.
- Model: `testapp/models/employee.py` expects `db.Model` and fields like `created_at = db.Column(db.DateTime, ...)` — ensure `db` is provided before using models.

---
If anything in these instructions is unclear or you want me to add example patches (e.g., adding `db` initialization or fixing `views.py` imports), tell me which part to update and I will draft a small, well-tested change. ✅
