from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

import models
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    total_incidents = db.query(models.Incident).count()
    triggered = db.query(models.Incident).filter(models.Incident.status == "triggered").count()
    acknowledged = db.query(models.Incident).filter(models.Incident.status == "acknowledged").count()
    resolved = db.query(models.Incident).filter(models.Incident.status == "resolved").count()
    total_services = db.query(models.Service).count()
    services_with_incidents = db.query(models.Service).filter(models.Service.status.in_(["critical", "warning"])).count()

    now = datetime.utcnow()
    on_call = db.query(models.OnCallShift).filter(
        models.OnCallShift.start <= now,
        models.OnCallShift.end >= now,
    ).count()

    return schemas.DashboardStats(
        total_incidents=total_incidents,
        triggered_incidents=triggered,
        acknowledged_incidents=acknowledged,
        resolved_incidents=resolved,
        total_services=total_services,
        services_with_incidents=services_with_incidents,
        on_call_users=on_call,
    )
