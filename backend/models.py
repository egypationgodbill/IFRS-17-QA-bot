from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base


class IncidentStatus(str, enum.Enum):
    triggered = "triggered"
    acknowledged = "acknowledged"
    resolved = "resolved"


class AlertStatus(str, enum.Enum):
    triggered = "triggered"
    resolved = "resolved"


class IncidentSeverity(str, enum.Enum):
    critical = "critical"
    high = "high"
    warning = "warning"
    info = "info"


class NotificationChannel(str, enum.Enum):
    email = "email"
    sms = "sms"
    push = "push"


# Association table for team members
team_members = Table(
    "team_members",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)

# Association table for escalation policy rules -> users
escalation_rule_users = Table(
    "escalation_rule_users",
    Base.metadata,
    Column("rule_id", Integer, ForeignKey("escalation_rules.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)

# Association table for incident responders
incident_responders = Table(
    "incident_responders",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incidents.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    phone = Column(String(20))
    time_zone = Column(String(50), default="UTC")
    role = Column(String(20), default="responder")  # admin, manager, responder
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    teams = relationship("Team", secondary=team_members, back_populates="members")
    on_call_shifts = relationship("OnCallShift", back_populates="user")
    acknowledged_incidents = relationship("Incident", secondary=incident_responders, back_populates="responders")
    notifications = relationship("Notification", back_populates="user")
    contact_methods = relationship("ContactMethod", back_populates="user")


class ContactMethod(Base):
    __tablename__ = "contact_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(20), nullable=False)  # email, sms, phone
    address = Column(String(200), nullable=False)  # email address or phone number
    label = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="contact_methods")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members = relationship("User", secondary=team_members, back_populates="teams")
    services = relationship("Service", back_populates="team")
    escalation_policies = relationship("EscalationPolicy", back_populates="team")


class EscalationPolicy(Base):
    __tablename__ = "escalation_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    team_id = Column(Integer, ForeignKey("teams.id"))
    repeat_enabled = Column(Boolean, default=False)
    num_loops = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="escalation_policies")
    rules = relationship("EscalationRule", back_populates="policy", order_by="EscalationRule.escalation_delay_in_minutes")
    services = relationship("Service", back_populates="escalation_policy")


class EscalationRule(Base):
    __tablename__ = "escalation_rules"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("escalation_policies.id"), nullable=False)
    escalation_delay_in_minutes = Column(Integer, default=30)

    policy = relationship("EscalationPolicy", back_populates="rules")
    targets = relationship("User", secondary=escalation_rule_users)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=True)
    schedule = relationship("Schedule")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    time_zone = Column(String(50), default="UTC")
    team_id = Column(Integer, ForeignKey("teams.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team")
    layers = relationship("ScheduleLayer", back_populates="schedule")
    shifts = relationship("OnCallShift", back_populates="schedule")


class ScheduleLayer(Base):
    __tablename__ = "schedule_layers"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    name = Column(String(100))
    rotation_type = Column(String(20), default="weekly")  # daily, weekly, custom
    rotation_turn_length_seconds = Column(Integer, default=604800)  # 1 week
    start = Column(DateTime(timezone=True), nullable=False)

    schedule = relationship("Schedule", back_populates="layers")
    users = relationship("ScheduleLayerUser", back_populates="layer")


class ScheduleLayerUser(Base):
    __tablename__ = "schedule_layer_users"

    id = Column(Integer, primary_key=True, index=True)
    layer_id = Column(Integer, ForeignKey("schedule_layers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position = Column(Integer, default=0)

    layer = relationship("ScheduleLayer", back_populates="users")
    user = relationship("User")


class OnCallShift(Base):
    __tablename__ = "on_call_shifts"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start = Column(DateTime(timezone=True), nullable=False)
    end = Column(DateTime(timezone=True), nullable=False)

    schedule = relationship("Schedule", back_populates="shifts")
    user = relationship("User", back_populates="on_call_shifts")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")  # active, warning, critical, maintenance
    escalation_policy_id = Column(Integer, ForeignKey("escalation_policies.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    integration_key = Column(String(100), unique=True, index=True)
    auto_resolve_timeout = Column(Integer, default=14400)  # seconds
    acknowledgement_timeout = Column(Integer, default=1800)  # seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    team = relationship("Team", back_populates="services")
    escalation_policy = relationship("EscalationPolicy", back_populates="services")
    incidents = relationship("Incident", back_populates="service")
    alerts = relationship("Alert", back_populates="service")
    integrations = relationship("Integration", back_populates="service")


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # generic, cloudwatch, datadog, etc.
    integration_key = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    service = relationship("Service", back_populates="integrations")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_number = Column(Integer, unique=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    status = Column(String(20), default=IncidentStatus.triggered)
    severity = Column(String(20), default=IncidentSeverity.critical)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    escalation_policy_id = Column(Integer, ForeignKey("escalation_policies.id"))
    resolved_at = Column(DateTime(timezone=True))
    acknowledged_at = Column(DateTime(timezone=True))
    last_status_change_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    service = relationship("Service", back_populates="incidents")
    created_by = relationship("User", foreign_keys=[created_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    escalation_policy = relationship("EscalationPolicy")
    responders = relationship("User", secondary=incident_responders, back_populates="acknowledged_incidents")
    alerts = relationship("Alert", back_populates="incident")
    notes = relationship("IncidentNote", back_populates="incident")
    timeline = relationship("IncidentTimelineEntry", back_populates="incident", order_by="IncidentTimelineEntry.created_at")
    notifications = relationship("Notification", back_populates="incident")


class IncidentNote(Base):
    __tablename__ = "incident_notes"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="notes")
    user = relationship("User")


class IncidentTimelineEntry(Base):
    __tablename__ = "incident_timeline"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    type = Column(String(50), nullable=False)  # triggered, acknowledged, resolved, escalated, note_added
    summary = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="timeline")
    user = relationship("User")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_key = Column(String(200), index=True)
    status = Column(String(20), default=AlertStatus.triggered)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    summary = Column(String(500))
    severity = Column(String(20), default=IncidentSeverity.critical)
    source = Column(String(200))
    body = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

    service = relationship("Service", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    type = Column(String(50), nullable=False)  # email, sms, push
    message = Column(Text)
    status = Column(String(20), default="pending")  # pending, sent, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="notifications")
    incident = relationship("Incident", back_populates="notifications")
