from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import asyncio
from typing import List

import models
from database import engine, SessionLocal
from auth import get_password_hash
from routes import auth, users, teams, services, incidents, alerts, escalations, schedules, dashboard

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PagerDuty Clone", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(services.router)
app.include_router(incidents.router)
app.include_router(alerts.router)
app.include_router(escalations.router)
app.include_router(schedules.router)
app.include_router(dashboard.router)


# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for c in dead:
            self.active_connections.remove(c)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/health")
def health():
    return {"status": "ok"}


def seed_demo_data():
    """Seed the database with demo data if empty."""
    db = SessionLocal()
    try:
        if db.query(models.User).count() > 0:
            return

        # Create admin user
        admin = models.User(
            name="Admin User",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            phone="+1-555-0100",
            role="admin",
        )
        db.add(admin)

        # Create responders
        alice = models.User(
            name="Alice Smith",
            email="alice@example.com",
            hashed_password=get_password_hash("password123"),
            phone="+1-555-0101",
            role="responder",
        )
        bob = models.User(
            name="Bob Jones",
            email="bob@example.com",
            hashed_password=get_password_hash("password123"),
            phone="+1-555-0102",
            role="responder",
        )
        carol = models.User(
            name="Carol Williams",
            email="carol@example.com",
            hashed_password=get_password_hash("password123"),
            phone="+1-555-0103",
            role="manager",
        )
        db.add_all([alice, bob, carol])
        db.flush()

        # Create team
        team = models.Team(name="Platform Engineering", description="Core infrastructure team")
        db.add(team)
        db.flush()
        team.members.extend([admin, alice, bob, carol])

        # Create escalation policy
        policy = models.EscalationPolicy(
            name="Default Escalation",
            description="Escalate to on-call, then manager",
            team_id=team.id,
            repeat_enabled=True,
            num_loops=2,
        )
        db.add(policy)
        db.flush()

        rule1 = models.EscalationRule(policy_id=policy.id, escalation_delay_in_minutes=30)
        db.add(rule1)
        db.flush()
        rule1.targets.append(alice)

        rule2 = models.EscalationRule(policy_id=policy.id, escalation_delay_in_minutes=60)
        db.add(rule2)
        db.flush()
        rule2.targets.append(carol)

        # Create services
        import secrets
        web_service = models.Service(
            name="Web Frontend",
            description="Main web application",
            status="active",
            escalation_policy_id=policy.id,
            team_id=team.id,
            integration_key=secrets.token_hex(16),
        )
        api_service = models.Service(
            name="API Gateway",
            description="REST API gateway",
            status="critical",
            escalation_policy_id=policy.id,
            team_id=team.id,
            integration_key=secrets.token_hex(16),
        )
        db_service = models.Service(
            name="Database Cluster",
            description="PostgreSQL primary cluster",
            status="active",
            escalation_policy_id=policy.id,
            team_id=team.id,
            integration_key=secrets.token_hex(16),
        )
        db.add_all([web_service, api_service, db_service])
        db.flush()

        # Create incidents
        from sqlalchemy import func
        from datetime import datetime, timezone, timedelta

        inc1 = models.Incident(
            incident_number=1,
            title="API Gateway returning 500 errors",
            description="Multiple customers reporting 500 errors on API calls",
            status="triggered",
            severity="critical",
            service_id=api_service.id,
            created_by_id=admin.id,
            escalation_policy_id=policy.id,
        )
        inc2 = models.Incident(
            incident_number=2,
            title="High memory usage on web servers",
            description="Memory usage above 90% on 3 web servers",
            status="acknowledged",
            severity="warning",
            service_id=web_service.id,
            created_by_id=admin.id,
            assigned_to_id=alice.id,
            escalation_policy_id=policy.id,
            acknowledged_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        inc3 = models.Incident(
            incident_number=3,
            title="Database connection pool exhausted",
            description="Connection pool at 100% capacity",
            status="resolved",
            severity="critical",
            service_id=db_service.id,
            created_by_id=admin.id,
            assigned_to_id=bob.id,
            escalation_policy_id=policy.id,
            resolved_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        db.add_all([inc1, inc2, inc3])
        db.flush()

        # Add timeline entries
        db.add(models.IncidentTimelineEntry(incident_id=inc1.id, type="triggered", summary="Incident triggered by monitoring"))
        db.add(models.IncidentTimelineEntry(incident_id=inc2.id, type="triggered", summary="Incident triggered by alerting system"))
        db.add(models.IncidentTimelineEntry(incident_id=inc2.id, type="acknowledged", summary=f"Acknowledged by {alice.name}", user_id=alice.id))
        db.add(models.IncidentTimelineEntry(incident_id=inc3.id, type="triggered", summary="Incident triggered by monitoring"))
        db.add(models.IncidentTimelineEntry(incident_id=inc3.id, type="acknowledged", summary=f"Acknowledged by {bob.name}", user_id=bob.id))
        db.add(models.IncidentTimelineEntry(incident_id=inc3.id, type="resolved", summary=f"Resolved by {bob.name}", user_id=bob.id))

        db.commit()
        print("Demo data seeded successfully")
    except Exception as e:
        db.rollback()
        print(f"Seeding error (may already exist): {e}")
    finally:
        db.close()


# Seed on startup
seed_demo_data()

# Serve frontend static files in production
frontend_dist = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
