"""
SQLAlchemy models for database
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy import TypeDecorator
from candig_dataset_service.orm.guid import GUID
from candig_dataset_service.orm import Base
import json


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


class Dataset(Base):
    """
    SQLAlchemy class representing datasets
    """
    __tablename__ = 'datasets'
    id = Column(GUID(), primary_key=True)
    version = Column(String(10), default="")
    tags = Column(JsonArray(), default=[])
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(100), default="")
    ontologies = Column(JsonArray(), default=[])
    ontologies_internal = Column(JsonArray(), default=[]) # Shorthand for searching/lookup

    created = Column(DateTime())
    __table_args__ = ()


class ChangeLog(Base):
    """
    SQLAlchemy class for listing changes to the database with version update
    """
    __tablename__ = 'changelogs'
    version = Column(String(10), primary_key=True)
    log = Column(JsonArray())
    created = Column(DateTime())
    __table_args__ = ()


class ActiveOntologies(Base):
    """
    SQLAlchemy class representing Ontologies in use
    """
    __tablename__ = 'active_ontologies'
    name = Column(String(10), primary_key=True)
    terms = Column(JsonArray(), default=[])

