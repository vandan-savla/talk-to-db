# Talk to DB

A full-stack AI-powered database querying application.

- Frontend: Next.js + TypeScript + Tailwind + Sonner notifications.
- Backend: FastAPI + Pydantic + SQLAlchemy + PostgreSQL + LangChain + Qdrant + vector search and agent workflow.
- AI query pipeline for natural language to SQL, schema awareness, validation, and results.

## Live Deployment

Hosted frontend URL:

- https://talk-to-db-frontend.vercel.app/login

> Backend API must be deployed separately and configured via `NEXT_PUBLIC_API_URL`.

---

## Repo Structure

- `backend/`
  - `api/main.py` - FastAPI app entrypoint.
  - `app/` - application modules, agent nodes, tools.
  - `database_migrations/` - initialization SQL and CSV fixtures.
  - `schema_worker/` - schema artifact generation/background worker.
  - `utils/connect.py` - database connection helpers.
  - `vector_store/` - qdrant vector storage glue.
  - `.env` - environment variables (not committed to GitHub in production).
- `frontend/`
  - `app/` - Next.js app routes and pages.
  - `components/` - UI components, chat flow.
  - `lib/` - provider/context utilities.
  - `public/` - static assets.

---

## Local Setup (Backend)

1. Clone repo and navigate:

```bash
git clone <repo-url>
cd "talk to db"/backend
```

2. Python environment:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

3. Database initialization:

For local PostgreSQL setup:

- Ensure `psql` is installed.
- On Windows, add `C:\Program Files\PostgreSQL\<version>\bin` to your `PATH`.
- Option 1 (recommended): run provided script from `backend`:

```bash
cd backend
# On macOS/Linux
chmod +x ./script.sh
./script.sh

# On Windows (PowerShell)
./script.sh
```

- Option 2: manually execute SQL in `database_migrations/sql`:

```bash
psql -h localhost -U postgres -d postgres -f database_migrations/sql/01_init_master_db.sql
psql -h localhost -U postgres -d postgres -f database_migrations/sql/02_master_schema.sql
psql -h localhost -U postgres -d postgres -f database_migrations/sql/01_init_app_db.sql
psql -h localhost -U postgres -d postgres -f database_migrations/sql/02_app_schema.sql
```

Load seed data:

```bash
python database_migrations/scripts/load_csv.py
```

4. Start backend server:

```bash
cd backend
.venv\Scripts\activate
uvicorn api.main:app --reload
```

5. Start schema worker (optional):

```bash
python -m schema_worker.schema_check_worker
```

---

## Local Setup (Frontend)

1. Navigate:

```bash
cd "talk to db"/frontend
npm install
```

2. Configure `.env` (or `.env.local`) with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run development server:

```bash
npm run dev
```

4. Open browser:

- http://localhost:3000/login

---

## Usage

- Register a new account (`/register`).
- Login and go to `/chat` for natural language query chat.
- `/explorer` for schema browsing and manual SQL query execution.

---

## Testing and Debugging

- Confirm API status: `http://localhost:8000/docs` (Swagger UI).
- Verify produced SQL from assistant path in UI.
- Watch backend logs for exceptions during query translation/exec.

---

## Troubleshooting

- If `api` import fails, ensure working directory is `backend` and package root has `__init__.py`.
- Inspect CORS configuration in `api/main.py` if frontend requests fail (allowed origins).
- Ensure Postgres is running and connection string matches `.env`.
