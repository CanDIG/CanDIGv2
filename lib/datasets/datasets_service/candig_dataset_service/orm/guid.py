"""
UUIDs for the database - from SQLAlchemy docs
"""
import uuid

from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    from SQLAlchemy Docs
    http://docs.sqlalchemy.org/en/rel_0_9/core/custom_types.html
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        """Dialect-specific implementation; use UUIDs for Postgres, otherwise CHAR"""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        """Process the value and return"""
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        """Process provided value"""
        if value is None:
            return value
        else:
            return uuid.UUID(value).hex
