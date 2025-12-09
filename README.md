# FastAPI Example Service

FastAPI + SQLAlchemy + PostgreSQL starter that provides user auth (JWT), posts, and voting APIs. Includes Docker and systemd deployment examples plus pytest suite.

## 1) Prerequisites
- Python 3.12+
- PostgreSQL (create app DB and a test DB, e.g. `fastapi` and `fastapi_test`)
- Optional: Docker & Docker Compose

## 2) Setup (local)
```bash
cd /home/cyapoon/fastapi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the project root (sample):
```env
DB_HOST=localhost
DB_USER=postgres
DB_PWD=postgres
DB_NAME=fastapi
SECRET_KEY=replace-with-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Prepare database: create the database, then run migrations if you use Alembic:
```bash
alembic upgrade head
```
(Alternatively rely on SQLAlchemy metadata creation on first run.)

## 3) Run the API locally
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Health check: `http://localhost:8000/`

## 4) Docker Compose
- Dev (hot reload, mounts local code, built-in Postgres):
```bash
docker compose -f docker-compose-dev.yml up --build
```
- Prod example (uses image tag `<user_name>/fastapi`; build or pull first):
```bash
docker build -t <user_name>/fastapi .
docker compose -f docker-compose-prod.yml up -d
```
Place `.env` in the repo root so the container can read DB and JWT settings.

## 5) Run tests
Uses pytest and a dedicated test DB named `${DB_NAME}_test`:
```bash
pytest
```
Ensure the test database exists and credentials in `.env` match.

## 6) Deploy to a remote VM
### Option A: Docker Compose (recommended)
1. Copy code and `.env` to the VM.
2. Install Docker and Docker Compose.
3. Build or pull image: `docker build -t <user_name>/fastapi .` (or `docker pull <user_name>/fastapi`).
4. Start: `docker compose -f docker-compose-prod.yml up -d`.
5. Open the desired port (default 8000) in firewall/security group or map to 80/443.

### Option B: systemd + Gunicorn
1. On the VM, create a venv and `pip install -r requirements.txt`.
2. Copy `fastapi.service` to `/etc/systemd/system/fastapi.service` and update paths:
   - `WorkingDirectory` → project path
   - `Environment` → venv bin path
   - `ExecStart` → adjust workers/port as needed
3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```
4. (Optional) Put Nginx in front for TLS and domain routing.

## 7) Project layout
- `app/main.py` – FastAPI entrypoint
- `app/routers/` – post/user/auth/vote routes
- `app/database.py` – DB engine and session
- `app/models.py` – SQLAlchemy models
- `app/schemas.py` – Pydantic schemas
- `tests/` – pytest suites and fixtures
- `docker-compose-*.yml`, `Dockerfile` – containerization
- `fastapi.service` – systemd unit example

## 8) CI/CD
- GitHub Actions workflow: `.github/workflows/build-deploy.yml`
  - Triggers on push/PR to `main`.
  - Build job spins up PostgreSQL service, installs deps, runs pytest with secrets-provided DB creds and JWT settings.
  - Deploy job (after build passes) SSHes to the target host (secrets: `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`), pulls latest code, installs deps, and restarts the systemd service (`fastapi`).
- Required secrets: `DB_PWD`, `DB_USER`, `DB_HOST`, `DB_NAME`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DB_URL`, `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`.
- Optional (commented) Docker publish steps can be enabled by adding `DOCKER_USERNAME` and `DOCKER_PASSWORD` and uncommenting the build/push steps.

