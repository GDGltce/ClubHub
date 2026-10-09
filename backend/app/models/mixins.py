"""
Shared mixin for all models: primary key, timestamps.
"""
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class UUID(TypeDecorator):
    """UUID that accepts strings from JWTs and URL params on SQLite."""

    impl = Uuid
    cache_ok = True

    def __init__(self, as_uuid: bool = True):
        super().__init__()
        self._as_uuid = as_uuid

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(Uuid(as_uuid=self._as_uuid))

    def process_bind_param(self, value, dialect):
        if value is None or isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Base(UUIDMixin, TimestampMixin):
    """Convenience base combining both mixins."""
    pass
