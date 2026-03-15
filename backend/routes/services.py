import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api/services", tags=["services"])


def _make_integration_key():
    return secrets.token_hex(16)


@router.get("/", response_model=List[schemas.ServiceOut])
def list_services(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Service).all()


@router.post("/", response_model=schemas.ServiceOut)
def create_service(service_in: schemas.ServiceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    service = models.Service(
        **service_in.model_dump(),
        integration_key=_make_integration_key(),
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/{service_id}", response_model=schemas.ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.put("/{service_id}", response_model=schemas.ServiceOut)
def update_service(
    service_id: int,
    service_in: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    for field, value in service_in.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()
    return {"message": "Service deleted"}


@router.get("/{service_id}/integrations", response_model=List[schemas.IntegrationOut])
def list_integrations(service_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Integration).filter(models.Integration.service_id == service_id).all()


@router.post("/{service_id}/integrations", response_model=schemas.IntegrationOut)
def create_integration(
    service_id: int,
    integration_in: schemas.IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    integration = models.Integration(
        service_id=service_id,
        name=integration_in.name,
        type=integration_in.type,
        integration_key=_make_integration_key(),
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration
