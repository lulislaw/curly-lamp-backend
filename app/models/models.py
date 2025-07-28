import datetime
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    JSON,
    text,
    func,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AppealType(Base):
    __tablename__ = "appeal_types"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    sort_order = Column(Integer, nullable=False)


class SeverityLevel(Base):
    __tablename__ = "severity_levels"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)


class AppealStatus(Base):
    __tablename__ = "appeal_statuses"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    sort_order = Column(Integer, nullable=False)

class Appeal(Base):
    __tablename__ = "appeals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    type_id = Column(Integer, ForeignKey("appeal_types.id"), nullable=False)
    severity_id = Column(Integer, ForeignKey("severity_levels.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("appeal_statuses.id"), nullable=False)
    location = Column(String(255))
    description = Column(Text)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    source = Column(String(50), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    payload = Column("metadata", JSON, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    reporter = relationship("User", foreign_keys=[reporter_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    history = relationship("AppealHistory", back_populates="appeal", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="appeal", cascade="all, delete-orphan")
    type = relationship("AppealType", lazy="joined")
    severity = relationship("SeverityLevel", lazy="joined")
    status = relationship("AppealStatus", lazy="joined")
    ticket_number = Column(
        Integer,
        nullable=False,
        server_default=text("nextval('appeals_ticket_number_seq'::regclass)")
    )

    @property
    def type_name(self) -> str:
        return self.type.name if self.type else None

    @property
    def severity_name(self) -> str:
        return self.severity.name if self.severity else None

    @property
    def status_name(self) -> str:
        return self.status.name if self.status else None


class AppealHistory(Base):
    __tablename__ = "appeal_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appeal_id = Column(UUID(as_uuid=True), ForeignKey("appeals.id", ondelete="NO ACTION"))
    event_time = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    event_type = Column(String(50), nullable=False)
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    field_name = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    comment = Column(Text)
    payload = Column("metadata", JSON, nullable=True)
    appeal = relationship("Appeal", back_populates="history")
    changed_by = relationship("User")


class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appeal_id = Column(UUID(as_uuid=True), ForeignKey("appeals.id", ondelete="CASCADE"), nullable=False)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    file_path = Column(String(1024), nullable=False)
    file_name = Column(String(255))
    file_size = Column(Integer)
    content_type = Column(String(100))
    uploaded_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    payload = Column("metadata", JSON, nullable=True)
    appeal = relationship("Appeal", back_populates="attachments")
    uploaded_by = relationship("User")


class CameraHardware(Base):
    __tablename__ = "camera_hardware"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    stream_url = Column(String, nullable=False)
    ptz_enabled = Column(Boolean, default=False)
    ptz_protocol = Column(String, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)


class Image(Base):
    __tablename__ = "images"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_at = Column(TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)


class BuildingConfig(Base):
    __tablename__ = 'building_config'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_build = Column(Integer, nullable=False)
    name_build = Column(Text, nullable=False)
    config = Column(JSONB, nullable=False, default={})
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)

role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
)

user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(50), unique=True, nullable=False, index=True)
    full_name     = Column(String(100))
    email         = Column(String(100), unique=True, nullable=False, index=True)
    phone         = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    tg_id         = Column(String(100), nullable=True)
    created_at    = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at    = Column(TIMESTAMP(timezone=True), server_default=func.now(),
                           onupdate=func.now(), nullable=False)

    roles = relationship('Role', secondary=user_roles, back_populates='users')


class Role(Base):
    __tablename__ = 'roles'

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at  = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at  = Column(TIMESTAMP(timezone=True), server_default=func.now(),
                         onupdate=func.now(), nullable=False)

    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')
    users       = relationship('User', secondary=user_roles, back_populates='roles')


class Permission(Base):
    __tablename__ = 'permissions'

    id          = Column(Integer, primary_key=True, index=True)
    code        = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at  = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at  = Column(TIMESTAMP(timezone=True), server_default=func.now(),
                         onupdate=func.now(), nullable=False)

    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')