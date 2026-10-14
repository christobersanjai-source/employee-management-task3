# Employee Management — Task 3: Employee & Team APIs

FastAPI CRUD APIs for an employee directory with validation, pagination, department filtering, search, team/direct-report lookups, soft delete, SQLAlchemy, PostgreSQL, Alembic and pytest.

## Features
- `POST /employees`, `GET /employees`, `GET /employees/{id}`, `PATCH /employees/{id}`, `DELETE /employees/{id}` (soft delete)
- `GET /departments`, `GET /departments/{id}/employees`, `GET /employees/{id}/team` (direct reports), `GET /roles`
- List query: `?page=1&size=20&department=1&q=name`; response includes `items`, `total`, `page`, `size`.
- Email validation and normalization, non-empty name, joining date cannot be in the future, unique email conflict handling.
- Shared JSON error shape `{ "error": "...", "message": "..." }`.
- Business logic in `app/services/employee_service.py`, not route handlers.

## Run locally with Docker (recommended)
1. Copy `.env.example` to `.env` in this folder. In PowerShell: `Copy-Item .env.example .env`
2. Ensure Docker Desktop is running.
3. From this folder run: `docker compose up --build -d`
4. Check: `docker compose ps` and `docker compose logs --tail 50 api`
5. Open `http://localhost:8000/docs`.

Compose starts PostgreSQL service named `db`, waits for its health check, runs `alembic upgrade head`, then starts the API. Run `docker compose down` only when you intentionally want to stop this stack; the named database volume is retained unless explicitly removed.

## Run tests
## Run tests

Create and activate a virtual environment, then install dependencies.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the test suite:

```powershell
python -m pytest -q
```

Expected result:

```text
10 passed
```

Tests use an isolated in-memory SQLite database and do not require Docker or PostgreSQL.
## Example requests
```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod 'http://localhost:8000/employees?page=1&size=20&department=1&q=Sanjai'
```
Create employee in Swagger `/docs` with JSON:
```json
{"full_name":"Sanjai Kumar","email":"sanjai@example.com","department_id":1,"manager_id":null,"role_ids":[1],"joining_date":"2026-10-01"}
```
Department and role IDs must already exist. Seed those through your database/SQL if needed.

## Database migration
- Apply: `alembic upgrade head`
- Roll back: `alembic downgrade base`

## Notes
This Task 3 package includes the Task 2 database models/migration as a standalone working base. Keep your original Task 1 and Task 2 folders unchanged until this version is verified, then merge/upload according to your internship repository structure.
