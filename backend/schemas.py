from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# --- Auth ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# --- User ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    time_zone: str = "UTC"
    role: str = "responder"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    time_zone: Optional[str] = None
    role: Optional[str] = None


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Contact Method ---
class ContactMethodCreate(BaseModel):
    type: str
    address: str
    label: Optional[str] = None


class ContactMethodOut(ContactMethodCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Team ---
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamOut(TeamBase):
    id: int
    created_at: datetime
    members: List[UserOut] = []

    class Config:
        from_attributes = True


# --- Escalation Rule ---
class EscalationRuleCreate(BaseModel):
    escalation_delay_in_minutes: int = 30
    target_user_ids: List[int] = []
    schedule_id: Optional[int] = None


class EscalationRuleOut(BaseModel):
    id: int
    escalation_delay_in_minutes: int
    targets: List[UserOut] = []
    schedule_id: Optional[int] = None

    class Config:
        from_attributes = True


# --- Escalation Policy ---
class EscalationPolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    team_id: Optional[int] = None
    repeat_enabled: bool = False
    num_loops: int = 0


class EscalationPolicyCreate(EscalationPolicyBase):
    rules: List[EscalationRuleCreate] = []


class EscalationPolicyOut(EscalationPolicyBase):
    id: int
    created_at: datetime
    rules: List[EscalationRuleOut] = []

    class Config:
        from_attributes = True


# --- Schedule Layer User ---
class ScheduleLayerUserCreate(BaseModel):
    user_id: int
    position: int = 0


class ScheduleLayerUserOut(BaseModel):
    id: int
    user_id: int
    position: int
    user: UserOut

    class Config:
        from_attributes = True


# --- Schedule Layer ---
class ScheduleLayerCreate(BaseModel):
    name: Optional[str] = None
    rotation_type: str = "weekly"
    rotation_turn_length_seconds: int = 604800
    start: datetime
    user_ids: List[int] = []


class ScheduleLayerOut(BaseModel):
    id: int
    name: Optional[str]
    rotation_type: str
    rotation_turn_length_seconds: int
    start: datetime
    users: List[ScheduleLayerUserOut] = []

    class Config:
        from_attributes = True


# --- Schedule ---
class ScheduleBase(BaseModel):
    name: str
    description: Optional[str] = None
    time_zone: str = "UTC"
    team_id: Optional[int] = None


class ScheduleCreate(ScheduleBase):
    layers: List[ScheduleLayerCreate] = []


class ScheduleOut(ScheduleBase):
    id: int
    created_at: datetime
    layers: List[ScheduleLayerOut] = []

    class Config:
        from_attributes = True


# --- On-Call Shift ---
class OnCallShiftOut(BaseModel):
    id: int
    schedule_id: int
    user: UserOut
    start: datetime
    end: datetime

    class Config:
        from_attributes = True


# --- Service ---
class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    escalation_policy_id: Optional[int] = None
    team_id: Optional[int] = None
    auto_resolve_timeout: int = 14400
    acknowledgement_timeout: int = 1800


class ServiceCreate(ServiceBase):
    pass


class ServiceOut(ServiceBase):
    id: int
    status: str
    integration_key: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Integration ---
class IntegrationCreate(BaseModel):
    name: str
    type: str


class IntegrationOut(IntegrationCreate):
    id: int
    service_id: int
    integration_key: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Alert ---
class AlertCreate(BaseModel):
    routing_key: str
    event_action: str  # trigger, resolve, acknowledge
    dedup_key: Optional[str] = None
    payload: dict


class AlertOut(BaseModel):
    id: int
    alert_key: Optional[str]
    status: str
    service_id: int
    incident_id: Optional[int]
    summary: Optional[str]
    severity: str
    source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Incident Note ---
class IncidentNoteCreate(BaseModel):
    content: str


class IncidentNoteOut(BaseModel):
    id: int
    incident_id: int
    content: str
    created_at: datetime
    user: UserOut

    class Config:
        from_attributes = True


# --- Incident Timeline ---
class TimelineEntryOut(BaseModel):
    id: int
    type: str
    summary: Optional[str]
    created_at: datetime
    user: Optional[UserOut]

    class Config:
        from_attributes = True


# --- Incident ---
class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "critical"
    service_id: int


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    assigned_to_id: Optional[int] = None


class IncidentOut(IncidentBase):
    id: int
    incident_number: int
    status: str
    assigned_to: Optional[UserOut]
    created_by: Optional[UserOut]
    service: ServiceOut
    escalation_policy: Optional[EscalationPolicyOut]
    responders: List[UserOut] = []
    resolved_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class IncidentDetail(IncidentOut):
    notes: List[IncidentNoteOut] = []
    timeline: List[TimelineEntryOut] = []
    alerts: List[AlertOut] = []


# --- Dashboard Stats ---
class DashboardStats(BaseModel):
    total_incidents: int
    triggered_incidents: int
    acknowledged_incidents: int
    resolved_incidents: int
    total_services: int
    services_with_incidents: int
    on_call_users: int
