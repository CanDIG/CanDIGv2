"""
SQLAlchemy models for database
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from candig_cnv_service.orm import Base
from candig_cnv_service.orm.custom_types import GUID, JsonArray, TimeStamp


class Patient(Base):
    """
    SQLAlchemy class representing a Patient
    """

    __tablename__ = "patient"

    patient_id = Column(GUID(), primary_key=True)
    sample_id = relationship("Sample")


class Sample(Base):
    """
    SQLAlchemy class representing a Sample tied to a Patient
    """

    __tablename__ = "sample"

    sample_id = Column(String(100), primary_key=True)
    patient_id = Column(
        GUID(), ForeignKey("patient.patient_id"), nullable=False
    )
    tags = Column(JsonArray(), default=[])
    description = Column(String(100), unique=True, nullable=False)
    created = Column(TimeStamp())
    cnv_id = relationship("CNV")


class CNV(Base):
    """
    SQLAlchemy class representing a collection of Copy Number
    Variants, all tied to a Sample
    """

    __tablename__ = "cnv"
    # cnv_id = Column(Integer, primary_key=True)

    sample_id = Column(
        String(100), ForeignKey("sample.sample_id"), primary_key=True
    )
    start_position = Column(Integer, primary_key=True)
    end_position = Column(Integer)
    copy_number = Column(Float)
    copy_number_ploidy_corrected = Column(Integer)
    chromosome_number = Column(String(100))
