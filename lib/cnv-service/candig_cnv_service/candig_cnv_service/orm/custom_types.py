import uuid
import json

from sqlalchemy import TypeDecorator, CHAR, String
from sqlalchemy.dialects.postgresql import UUID


class TimeStamp(TypeDecorator):
    impl = String(14)

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return value


class GUID(TypeDecorator):

    impl = CHAR

    def load_dialect_impl(self, dialect):
        """Dialect-specific implementation;
           use UUIDs for Postgres, otherwise CHAR"""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        """Process the value and return"""
        if value is None:
            return value
        elif dialect.name == "postgresql":
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


class JsonArray(TypeDecorator):
    """
    Custom array type to emulate arrays in sqlite3
    """

    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

    def copy(self):
        return JsonArray(self.impl.length)
