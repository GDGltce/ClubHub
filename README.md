# ClubHub 🎓

Google Developer Groups on Campus LTCE

---

## What is ClubHub?

A single platform where a college registers itself, every club keeps its complete history in one place, and every student can discover clubs, join them, and follow their activity.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite, React Router v6, Axios |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL (Supabase) |
| Auth | JWT (HS256) – temporary default login |
| Styling | CSS Variables + Google Fonts |

---

## Folder Structure

```
ClubHub/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py         # Dependency injection (auth guards)
│   │   │   └── v1/
│   │   │       ├── router.py   # Aggregates all routers
│   │   │       └── endpoints/  # One file per module
│   │   │           ├── auth.py
│   │   │           ├── institutions.py
│   │   │           ├── clubs.py
│   │   │           ├── memberships.py
│   │   │           ├── events.py
│   │   │           ├── documents.py
│   │   │           ├── meetings.py
│   │   │           └── notifications.py
│   │   ├── core/
│   │   │   ├── config.py       # Pydantic settings (.env)
│   │   │   └── security.py     # JWT + bcrypt
│   │   ├── db/
│   │   │   ├── session.py      # SQLAlchemy engine + get_db
│   │   │   └── base.py         # Alembic model registry
│   │   ├── models/             # SQLAlchemy ORM models (1 file = 1 module)
│   │   │   ├── institution.py  # College, Department
│   │   │   ├── club.py         # Club
│   │   │   ├── user.py         # User, UserProfile
│   │   │   ├── membership.py   # JoinRequest, Membership, CommitteeTerm
│   │   │   ├── event.py        # Event, EventStage
│   │   │   ├── document.py     # Document
│   │   │   ├── finance.py      # Budget, Expense, Income
│   │   │   ├── media.py        # Album, Photo
│   │   │   ├── meeting.py      # Meeting, AgendaItem, Decision, Task
│   │   │   ├── content.py      # ContentPlan, PostEntry
│   │   │   ├── notification.py # Notification
│   │   │   └── audit.py        # ActivityLog
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic (future)
│   │   └── main.py             # FastAPI app entrypoint
│   ├── migrations/             # Alembic migrations
│   ├── tests/
│   ├── seed.py                 # Dev seed data
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                   # React + Vite application
    ├── src/
    │   ├── api/                # Axios API client + modules
    │   ├── components/         # Shared UI components
    │   │   ├── common/         # Button, Card, Badge, Modal…
    │   │   └── layout/         # Navbar, Sidebar, Footer
    │   ├── contexts/           # AuthContext, NotificationContext
    │   ├── hooks/              # useAuth, useClub, useEvent…
    │   ├── pages/              # Route-level page components
    │   │   ├── auth/           # Login, Register
    │   │   ├── dashboard/      # Home dashboard
    │   │   ├── clubs/          # ClubDirectory, ClubDetail, ClubManage
    │   │   ├── events/         # EventList, EventDetail, EventCreate
    │   │   ├── meetings/       # MeetingList, MeetingDetail
    │   │   └── admin/          # Platform admin pages
    │   ├── router/             # React Router configuration
    │   ├── styles/             # Global CSS, design tokens
    │   └── utils/              # Helpers, constants
    ├── index.html
    └── vite.config.js
```

---

## Quick Start

### 1. Backend

SQLite is the default, so a fresh clone runs without Docker or PostgreSQL.

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# Windows: copy .env.example .env
# macOS/Linux: cp .env.example .env

python seed.py
uvicorn app.main:app --port 8000
```

To use PostgreSQL or Supabase instead, set `DATABASE_URL` in `.env` and run `alembic upgrade head` before seeding. Python 3.13 is supported with the pinned requirements.

API docs → http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App → http://localhost:5173

---

## Default Login (Dev)

| Role | Email | Password |
|------|-------|---------|
| Platform Admin | `admin@clubhub.dev` | `admin1234` |

Use the `/api/v1/auth/register` endpoint to create more users.

---

## Core Modules

| # | Module | Endpoint prefix |
|---|--------|----------------|
| 1 | Institution Registry | `/api/v1/institutions` |
| 2 | Auth & Profiles | `/api/v1/auth` |
| 3 | Membership | `/api/v1/memberships` |
| 4 | Events | `/api/v1/events` |
| 5 | Document Vault | `/api/v1/documents` |
| 6 | Finance Log | *(schemas ready, endpoints TBD)* |
| 7 | Media Gallery | *(schemas ready, endpoints TBD)* |
| 8 | Meetings | `/api/v1/meetings` |
| 9 | Content Planner | *(schemas ready, endpoints TBD)* |
| 10 | Notifications | `/api/v1/notifications` |

---

## Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **Settings → Database → Connection string (URI)**
3. Replace `DATABASE_URL` in `.env` with the Supabase URI
4. Run `alembic upgrade head`

---

## Contributing (Workshop Guide)

- **One module = one folder** → fewer merge conflicts
- Each module has its own model file, schema file, and endpoint file
- Branch naming: `feat/<module>-<your-name>`, e.g. `feat/finance-priya`
- PR must pass `uvicorn app.main:app` without errors before merge

---

## License

MIT — Free for educational use.
