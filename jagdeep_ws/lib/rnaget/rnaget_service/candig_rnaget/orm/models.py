"""
SQLAlchemy models for the database
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy import TypeDecorator
from candig_rnaget.orm.guid import GUID
from candig_rnaget.orm import Base
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


class Project(Base):
    """
    SQLAlchemy class/table representing projects
    """
    __tablename__ = 'projects'
    id = Column(GUID(), primary_key=True)
    version = Column(String(10), default="")
    tags = Column(JsonArray(), default=[])
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(100), default="")
    created = Column(DateTime())
    __table_args__ = ()


class Study(Base):
    """
    SQLAlchemy class/table representing studies
    """
    __tablename__ = 'studies'
    id = Column(GUID(), primary_key=True)
    version = Column(String(10), default="")
    tags = Column(JsonArray(), default=[])
    name = Column(String(100), nullable=False)
    description = Column(String(100), default="")
    parentProjectID = Column(GUID(), ForeignKey('projects.id'), nullable=False)
    patientList = Column(JsonArray(), default=[])
    sampleList = Column(JsonArray(), default=[])
    created = Column(DateTime())
    __table_args__ = (
        UniqueConstraint("parentProjectID", "name"),
    )


class Expression(Base):
    """
    Expressions stored in files table now. This table may be deprecated soon.
    """
    __tablename__ = 'expressions'
    __filepath__ = Column(String(100))
    id = Column(GUID(), primary_key=True)
    URL = Column(String(100))
    studyID = Column(GUID(), ForeignKey('studies.id'))
    created = Column(DateTime())
    version = Column(String(10), default="")
    tags = Column(JsonArray())
    __table_args__ = ()


class ChangeLog(Base):
    """
    SQLAlchemy class/table for listing changes to the database with version update
    """
    __tablename__ = 'changelogs'
    version = Column(String(10), primary_key=True)
    log = Column(JsonArray())
    created = Column(DateTime())
    __table_args__ = ()


class File(Base):
    """
    SQLAlchemy class/table for representing files
    """
    __tablename__ = 'files'
    __filepath__ = Column(String(100))
    id = Column(GUID(), primary_key=True)
    version = Column(String(10))
    tags = Column(JsonArray())
    fileType = Column(String(10))
    studyID = Column(GUID(), ForeignKey('studies.id'))
    url = Column(String(100), unique=True)
    units = Column(String(10))
    created = Column(DateTime())
    md5 = Column(String(16))
    headers = Column(JsonArray())
    __table_args__ = ()


class TempFile(Base):
    """
    SQLAlchemy class/table for representing temporary files. Table should be periodically cleared.
    """
    __tablename__ = 'tempfiles'
    __filepath__ = Column(String(100))
    id = Column(GUID(), primary_key=True)
    version = Column(String(10))
    fileType = Column(String(10))
    studyID = Column(GUID(), ForeignKey('studies.id'))
    url = Column(String(100))
    units = Column(String(10))
    created = Column(DateTime())
    md5 = Column(String(16))
    headers = Column(JsonArray())
    __table_args__ = ()
