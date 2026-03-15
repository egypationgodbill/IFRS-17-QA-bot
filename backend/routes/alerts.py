from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timezone

import models
import schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _next_incident_number(db: Session) -> int:
    result = db.query(func.max(models.Incident.incident_number)).scalar()
    return (result or 0) + 1


@router.post("/events")
def ingest_event(event: schemas.AlertCreate, db: Session = Depends(get_db)):
    """Ingest Events API v2 - compatible endpoint for creating/resolving alerts."""
    service = db.query(models.Service).filter(
        models.Service.integration_key == event.routing_key
    ).first()
    if not service:
        # Try integration key
        integration = db.query(models.Integration).filter(
            models.Integration.integration_key == event.routing_key
        ).first()
        if integration:
            service = integration.service
    if not service:
        raise HTTPException(status_code=400, detail="Invalid routing key")

    dedup_key = event.dedup_key or event.payload.get("custom_details", {}).get("dedup_key")
    payload = event.payload

    if event.event_action == "trigger":
        # Create or reopen alert
        alert = None
        if dedup_key:
            alert = db.query(models.Alert).filter(
                models.Alert.service_id == service.id,
                models.Alert.alert_key == dedup_key,
                models.Alert.status == models.AlertStatus.triggered,
            ).first()

        if not alert:
            alert = models.Alert(
                alert_key=dedup_key,
                service_id=service.id,
                summary=payload.get("summary", "Alert triggered"),
                severity=payload.get("severity", "critical"),
                source=payload.get("source"),
                body=str(payload.get("custom_details", {})),
                status=models.AlertStatus.triggered,
            )
            db.add(alert)
            db.flush()

            # Create incident
            incident = models.Incident(
                incident_number=_next_incident_number(db),
                title=payload.get("summary", f"Alert from {service.name}"),
                description=str(payload.get("custom_details", "")),
                severity=payload.get("severity", "critical"),
                service_id=service.id,
                escalation_policy_id=service.escalation_policy_id,
                status=models.IncidentStatus.triggered,
            )
            db.add(incident)
            db.flush()
            alert.incident_id = incident.id
            service.status = "critical"

        db.commit()
        return {"status": "success", "message": "Event processed", "dedup_key": dedup_key or str(alert.id)}

    elif event.event_action == "resolve":
        alerts = db.query(models.Alert).filter(
            models.Alert.service_id == service.id,
            models.Alert.status == models.AlertStatus.triggered,
        )
        if dedup_key:
            alerts = alerts.filter(models.Alert.alert_key == dedup_key)
        alerts = alerts.all()
        now = datetime.now(timezone.utc)
        for alert in alerts:
            alert.status = models.AlertStatus.resolved
            alert.resolved_at = now
            if alert.incident:
                alert.incident.status = models.IncidentStatus.resolved
                alert.incident.resolved_at = now
        db.commit()
        return {"status": "success", "message": "Alert resolved"}

    elif event.event_action == "acknowledge":
        alerts = db.query(models.Alert).filter(
            models.Alert.service_id == service.id,
            models.Alert.status == models.AlertStatus.triggered,
        )
        if dedup_key:
            alerts = alerts.filter(models.Alert.alert_key == dedup_key)
        for alert in alerts.all():
            if alert.incident and alert.incident.status == models.IncidentStatus.triggered:
                alert.incident.status = models.IncidentStatus.acknowledged
                alert.incident.acknowledged_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "success", "message": "Alert acknowledged"}

    raise HTTPException(status_code=400, detail="Invalid event_action")


@router.get("/")
def list_alerts(
    service_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Alert)
    if service_id:
        q = q.filter(models.Alert.service_id == service_id)
    if status:
        q = q.filter(models.Alert.status == status)
    return q.order_by(models.Alert.created_at.desc()).limit(100).all()
