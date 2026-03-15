from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

import models
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.get("/", response_model=List[schemas.ScheduleOut])
def list_schedules(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Schedule).all()


@router.post("/", response_model=schemas.ScheduleOut)
def create_schedule(schedule_in: schemas.ScheduleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    schedule = models.Schedule(
        name=schedule_in.name,
        description=schedule_in.description,
        time_zone=schedule_in.time_zone,
        team_id=schedule_in.team_id,
    )
    db.add(schedule)
    db.flush()

    for layer_in in schedule_in.layers:
        layer = models.ScheduleLayer(
            schedule_id=schedule.id,
            name=layer_in.name,
            rotation_type=layer_in.rotation_type,
            rotation_turn_length_seconds=layer_in.rotation_turn_length_seconds,
            start=layer_in.start,
        )
        db.add(layer)
        db.flush()
        for i, uid in enumerate(layer_in.user_ids):
            lu = models.ScheduleLayerUser(layer_id=layer.id, user_id=uid, position=i)
            db.add(lu)

    db.commit()
    db.refresh(schedule)
    _generate_shifts(db, schedule)
    return schedule


@router.get("/oncall", response_model=List[schemas.OnCallShiftOut])
def get_oncall(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    now = datetime.utcnow()
    shifts = db.query(models.OnCallShift).filter(
        models.OnCallShift.start <= now,
        models.OnCallShift.end >= now,
    ).all()
    return shifts


@router.get("/{schedule_id}", response_model=schemas.ScheduleOut)
def get_schedule(schedule_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.get("/{schedule_id}/shifts", response_model=List[schemas.OnCallShiftOut])
def get_shifts(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.OnCallShift).filter(models.OnCallShift.schedule_id == schedule_id).order_by(models.OnCallShift.start).all()


@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted"}


def _generate_shifts(db: Session, schedule: models.Schedule):
    """Generate on-call shifts for the next 90 days from schedule layers."""
    now = datetime.utcnow()
    end_date = now + timedelta(days=90)

    for layer in schedule.layers:
        users = sorted(layer.users, key=lambda u: u.position)
        if not users:
            continue
        turn_seconds = layer.rotation_turn_length_seconds
        current = layer.start
        user_idx = 0
        while current < end_date:
            shift_end = current + timedelta(seconds=turn_seconds)
            shift = models.OnCallShift(
                schedule_id=schedule.id,
                user_id=users[user_idx % len(users)].user_id,
                start=current,
                end=shift_end,
            )
            db.add(shift)
            current = shift_end
            user_idx += 1

    db.commit()
