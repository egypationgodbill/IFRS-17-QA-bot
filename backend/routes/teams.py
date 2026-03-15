from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("/", response_model=List[schemas.TeamOut])
def list_teams(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Team).all()


@router.post("/", response_model=schemas.TeamOut)
def create_team(team_in: schemas.TeamCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    team = models.Team(**team_in.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.get("/{team_id}", response_model=schemas.TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.put("/{team_id}", response_model=schemas.TeamOut)
def update_team(team_id: int, team_in: schemas.TeamCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    for field, value in team_in.model_dump(exclude_unset=True).items():
        setattr(team, field, value)
    db.commit()
    db.refresh(team)
    return team


@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()
    return {"message": "Team deleted"}


@router.post("/{team_id}/members/{user_id}")
def add_member(team_id: int, user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user not in team.members:
        team.members.append(user)
        db.commit()
    return {"message": "Member added"}


@router.delete("/{team_id}/members/{user_id}")
def remove_member(team_id: int, user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user and user in team.members:
        team.members.remove(user)
        db.commit()
    return {"message": "Member removed"}
