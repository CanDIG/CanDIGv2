import os
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4
from flask import current_app
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from chord_drs.backend import get_backend
from chord_drs.backends.minio import MinioBackend
from chord_drs.constants import SERVICE_NAME
from chord_drs.db import db
from chord_drs.utils import drs_file_checksum


class DrsMixin:
    # TODO: tried refactoring the id inside this mixin except
    # sqlalchemy is confused when using DrsMixin.id for remote_side below
    created = db.Column(db.DateTime, server_default=func.now())
    checksum = db.Column(db.String(64), nullable=False)
    size = db.Column(db.Integer, default=0)
    name = db.Column(db.String(250), nullable=True)
    description = db.Column(db.String(1000), nullable=True)


class DrsBundle(db.Model, DrsMixin):
    ___tablename__ = "drs_bundle"
    id = db.Column(db.String, primary_key=True)
    parent_bundle_id = db.Column(db.Integer, db.ForeignKey("drs_bundle.id"))
    parent_bundle = relationship("DrsBundle", remote_side=[id])
    objects = relationship("DrsObject", cascade="all, delete-orphan", backref="bundle")

    def __init__(self, *args, **kwargs):
        self.id = str(uuid4())
        super().__init__(*args, **kwargs)

    def update_checksum_and_size(self):
        checksums = []
        total_size = 0

        for obj in self.objects:
            total_size += obj.size
            checksums.append(obj.checksum)

        checksums.sort()
        concat_checksums = "".join(checksums)

        hash_obj = sha256()
        hash_obj.update(concat_checksums.encode())

        self.checksum = hash_obj.hexdigest()
        self.size = total_size


class DrsObject(db.Model, DrsMixin):
    id = db.Column(db.String, primary_key=True)
    bundle_id = db.Column(db.Integer, db.ForeignKey(DrsBundle.id), nullable=True)
    location = db.Column(db.String(500), nullable=False)

    def __init__(self, *args, **kwargs):
        location = kwargs.get("location")
        p = Path(location)

        if not p.exists():
            # TODO: we will need to account for URLs at some point
            raise Exception("Provided file path does not exists")

        self.id = str(uuid4())
        self.name = p.name
        new_filename = f"{self.id[:12]}-{p.name}"

        backend = get_backend()

        if not backend:
            raise Exception("The backend for this instance is not properly configured.")
        try:
            current_location = backend.save(location, new_filename)
        except Exception as e:
            current_app.logger.error(f"[{SERVICE_NAME}] Encountered exception during DRS object creation: {e}")
            # TODO: implement more specific exception handling
            raise Exception("Well if the file is not saved... we can't do squat")

        self.location = current_location
        del kwargs["location"]

        self.size = os.path.getsize(location)
        self.checksum = drs_file_checksum(location)

        super().__init__(*args, **kwargs)

    def return_minio_object(self):
        parsed_url = urlparse(self.location)

        if parsed_url.scheme != "s3":
            return None

        backend = get_backend()

        if not backend or not isinstance(backend, MinioBackend):
            raise Exception("The backend for this instance is not properly configured.")

        return backend.get_minio_object(self.location)
