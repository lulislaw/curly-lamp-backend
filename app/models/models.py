# backend/app/models/models.py

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
    JSON
)
from sqlalchemy.dialects.postgresql import UUID
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


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Appeal(Base):
    __tablename__ = "appeals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)

    type_id     = Column(Integer, ForeignKey("appeal_types.id"), nullable=False)
    severity_id = Column(Integer, ForeignKey("severity_levels.id"), nullable=False)
    status_id   = Column(Integer, ForeignKey("appeal_statuses.id"), nullable=False)

    location = Column(String(255))
    description = Column(Text)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    source = Column(String(50), nullable=False)

    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    payload = Column("metadata", JSON, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)


    reporter = relationship("User", foreign_keys=[reporter_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    history = relationship("AppealHistory", back_populates="appeal", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="appeal", cascade="all, delete-orphan")
    type = relationship("AppealType", lazy="joined")
    severity = relationship("SeverityLevel", lazy="joined")
    status = relationship("AppealStatus", lazy="joined")

    @property
    def type_name(self) -> str:
        """
        Возвращает human-readable название типа обращения, полученное через отношение type.
        """
        # self.type — объект модели AppealType (или None, если связи нет)
        return self.type.name if self.type else None  # или "" вместо None, если хотите строку
    @property
    def severity_name(self) -> str:
        """
        Возвращает human-readable название уровня серьезности через отношение severity.
        """
        return self.severity.name if self.severity else None

    @property
    def status_name(self) -> str:
        """
        Возвращает human-readable название статуса через отношение status.
        """
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
