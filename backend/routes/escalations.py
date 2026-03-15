from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/api/escalation-policies", tags=["escalation_policies"])


@router.get("/", response_model=List[schemas.EscalationPolicyOut])
def list_policies(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.EscalationPolicy).all()


@router.post("/", response_model=schemas.EscalationPolicyOut)
def create_policy(policy_in: schemas.EscalationPolicyCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    policy = models.EscalationPolicy(
        name=policy_in.name,
        description=policy_in.description,
        team_id=policy_in.team_id,
        repeat_enabled=policy_in.repeat_enabled,
        num_loops=policy_in.num_loops,
    )
    db.add(policy)
    db.flush()

    for rule_in in policy_in.rules:
        rule = models.EscalationRule(
            policy_id=policy.id,
            escalation_delay_in_minutes=rule_in.escalation_delay_in_minutes,
            schedule_id=rule_in.schedule_id,
        )
        db.add(rule)
        db.flush()
        for uid in rule_in.target_user_ids:
            user = db.query(models.User).filter(models.User.id == uid).first()
            if user:
                rule.targets.append(user)

    db.commit()
    db.refresh(policy)
    return policy


@router.get("/{policy_id}", response_model=schemas.EscalationPolicyOut)
def get_policy(policy_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    policy = db.query(models.EscalationPolicy).filter(models.EscalationPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/{policy_id}", response_model=schemas.EscalationPolicyOut)
def update_policy(
    policy_id: int,
    policy_in: schemas.EscalationPolicyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    policy = db.query(models.EscalationPolicy).filter(models.EscalationPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    policy.name = policy_in.name
    policy.description = policy_in.description
    policy.team_id = policy_in.team_id
    policy.repeat_enabled = policy_in.repeat_enabled
    policy.num_loops = policy_in.num_loops

    # Delete old rules
    for rule in policy.rules:
        db.delete(rule)
    db.flush()

    for rule_in in policy_in.rules:
        rule = models.EscalationRule(
            policy_id=policy.id,
            escalation_delay_in_minutes=rule_in.escalation_delay_in_minutes,
            schedule_id=rule_in.schedule_id,
        )
        db.add(rule)
        db.flush()
        for uid in rule_in.target_user_ids:
            user = db.query(models.User).filter(models.User.id == uid).first()
            if user:
                rule.targets.append(user)

    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/{policy_id}")
def delete_policy(policy_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    policy = db.query(models.EscalationPolicy).filter(models.EscalationPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(policy)
    db.commit()
    return {"message": "Policy deleted"}
