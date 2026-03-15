from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone

import models
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


def _next_incident_number(db: Session) -> int:
    result = db.query(func.max(models.Incident.incident_number)).scalar()
    return (result or 0) + 1


def _add_timeline(db: Session, incident_id: int, type: str, summary: str, user_id: Optional[int] = None):
    entry = models.IncidentTimelineEntry(
        incident_id=incident_id,
        type=type,
        summary=summary,
        user_id=user_id,
    )
    db.add(entry)


@router.get("/", response_model=List[schemas.IncidentOut])
def list_incidents(
    status: Optional[str] = None,
    service_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Incident)
    if status:
        q = q.filter(models.Incident.status == status)
    if service_id:
        q = q.filter(models.Incident.service_id == service_id)
    return q.order_by(models.Incident.created_at.desc()).all()


@router.post("/", response_model=schemas.IncidentOut)
def create_incident(
    incident_in: schemas.IncidentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    service = db.query(models.Service).filter(models.Service.id == incident_in.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    incident = models.Incident(
        incident_number=_next_incident_number(db),
        title=incident_in.title,
        description=incident_in.description,
        severity=incident_in.severity,
        service_id=incident_in.service_id,
        created_by_id=current_user.id,
        escalation_policy_id=service.escalation_policy_id,
        status=models.IncidentStatus.triggered,
    )
    db.add(incident)
    db.flush()
    _add_timeline(db, incident.id, "triggered", f"Incident triggered by {current_user.name}", current_user.id)

    # Update service status
    service.status = "critical"
    db.commit()
    db.refresh(incident)
    return incident


@router.get("/{incident_id}", response_model=schemas.IncidentDetail)
def get_incident(incident_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/{incident_id}", response_model=schemas.IncidentOut)
def update_incident(
    incident_id: int,
    update: schemas.IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    now = datetime.now(timezone.utc)
    old_status = incident.status

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)

    if update.status and update.status != old_status:
        incident.last_status_change_at = now
        if update.status == models.IncidentStatus.acknowledged:
            incident.acknowledged_at = now
            if current_user not in incident.responders:
                incident.responders.append(current_user)
            _add_timeline(db, incident.id, "acknowledged", f"Acknowledged by {current_user.name}", current_user.id)
        elif update.status == models.IncidentStatus.resolved:
            incident.resolved_at = now
            _add_timeline(db, incident.id, "resolved", f"Resolved by {current_user.name}", current_user.id)
            # Check if all incidents for service are resolved
            open_incidents = db.query(models.Incident).filter(
                models.Incident.service_id == incident.service_id,
                models.Incident.status != models.IncidentStatus.resolved,
                models.Incident.id != incident_id,
            ).count()
            if open_incidents == 0:
                service = db.query(models.Service).filter(models.Service.id == incident.service_id).first()
                if service:
                    service.status = "active"

    db.commit()
    db.refresh(incident)
    return incident


@router.post("/{incident_id}/acknowledge", response_model=schemas.IncidentOut)
def acknowledge_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.status == models.IncidentStatus.triggered:
        incident.status = models.IncidentStatus.acknowledged
        incident.acknowledged_at = datetime.now(timezone.utc)
        incident.assigned_to_id = current_user.id
        if current_user not in incident.responders:
            incident.responders.append(current_user)
        _add_timeline(db, incident.id, "acknowledged", f"Acknowledged by {current_user.name}", current_user.id)
        db.commit()
        db.refresh(incident)
    return incident


@router.post("/{incident_id}/resolve", response_model=schemas.IncidentOut)
def resolve_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.status != models.IncidentStatus.resolved:
        incident.status = models.IncidentStatus.resolved
        incident.resolved_at = datetime.now(timezone.utc)
        _add_timeline(db, incident.id, "resolved", f"Resolved by {current_user.name}", current_user.id)

        open_incidents = db.query(models.Incident).filter(
            models.Incident.service_id == incident.service_id,
            models.Incident.status != models.IncidentStatus.resolved,
            models.Incident.id != incident_id,
        ).count()
        if open_incidents == 0:
            service = db.query(models.Service).filter(models.Service.id == incident.service_id).first()
            if service:
                service.status = "active"

        db.commit()
        db.refresh(incident)
    return incident


@router.post("/{incident_id}/notes", response_model=schemas.IncidentNoteOut)
def add_note(
    incident_id: int,
    note_in: schemas.IncidentNoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    note = models.IncidentNote(incident_id=incident_id, user_id=current_user.id, content=note_in.content)
    db.add(note)
    _add_timeline(db, incident_id, "note_added", f"Note added by {current_user.name}", current_user.id)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{incident_id}/notes", response_model=List[schemas.IncidentNoteOut])
def list_notes(incident_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.IncidentNote).filter(models.IncidentNote.incident_id == incident_id).all()
