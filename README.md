# PagerDuty Clone

A full-featured incident management and on-call scheduling platform built with FastAPI + React.

## Features

- **Incident Management** — Create, acknowledge, resolve incidents with full timeline
- **Alert Ingestion** — Events API v2 compatible endpoint (`POST /api/alerts/events`)
- **Services** — Define monitored services with unique integration keys
- **On-Call Schedules** — Rotation-based schedules with shift generation
- **Escalation Policies** — Multi-level escalation rules with configurable delays
- **Teams & Users** — User management with roles (admin, manager, responder)
- **Dashboard** — Real-time stats on incidents and on-call coverage
- **WebSocket** — Live updates via `/ws`

## Quick Start

```bash
bash start.sh
```

Or start individually:

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Access the app at `http://localhost:3000`

## Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@example.com | admin123 | Admin |
| alice@example.com | password123 | Responder |
| bob@example.com | password123 | Responder |
| carol@example.com | password123 | Manager |

## API

Interactive API docs at `http://localhost:8000/docs`

### Alert Events API

```bash
curl -X POST http://localhost:8000/api/alerts/events \
  -H "Content-Type: application/json" \
  -d '{
    "routing_key": "<service_integration_key>",
    "event_action": "trigger",
    "payload": {
      "summary": "Database connection pool exhausted",
      "severity": "critical",
      "source": "prod-db-01"
    }
  }'
```

Actions: `trigger`, `resolve`, `acknowledge`

## Architecture

```
backend/
  main.py          FastAPI app + demo seed data
  models.py        SQLAlchemy ORM models
  schemas.py       Pydantic request/response schemas
  auth.py          JWT authentication
  routes/
    auth.py        Login, register, /me
    users.py       User CRUD + contact methods
    teams.py       Team management
    services.py    Service CRUD + integrations
    incidents.py   Incident lifecycle
    alerts.py      Alert ingestion (Events API v2)
    schedules.py   On-call schedules + shift generation
    escalations.py Escalation policy management
    dashboard.py   Stats endpoint

frontend/
  src/
    pages/         Dashboard, Incidents, Services, etc.
    components/    Layout, StatusBadge, SeverityDot
    hooks/         useAuth
    api.js         Axios instance with auth interceptor
```
