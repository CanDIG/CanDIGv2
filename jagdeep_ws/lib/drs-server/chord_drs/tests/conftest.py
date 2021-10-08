import os

import boto3
from flask import g
from moto import mock_s3
import pytest
from pytest_lazyfixture import lazy_fixture

from chord_drs.app import application, db
from chord_drs.backends.base import FakeBackend
from chord_drs.backends.minio import MinioBackend
from chord_drs.config import BASEDIR, APP_DIR
from chord_drs.commands import create_drs_bundle
from chord_drs.models import DrsObject


SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
NON_EXISTENT_DUMMY_FILE = os.path.join(BASEDIR, "potato")
DUMMY_FILE = os.path.join(BASEDIR, "README.md")
DUMMY_DIRECTORY = os.path.join(APP_DIR, "migrations")


@pytest.fixture
def client_minio():
    bucket_name = "test"
    application.config["MINIO_URL"] = "http://127.0.0.1:9000"
    application.config["MINIO_BUCKET"] = bucket_name
    application.config["SERVICE_DATA_SOURCE"] = "minio"

    with application.app_context(), mock_s3():
        s3 = boto3.resource("s3", region_name="ca-central-1")
        minio_backend = MinioBackend(resource=s3)
        g.backend = minio_backend

        s3.create_bucket(Bucket=bucket_name)
        db.create_all()

        yield application.test_client()

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client_local():
    application.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

    with application.app_context():
        g.backend = FakeBackend()

        db.create_all()

        yield application.test_client()

        db.session.remove()
        db.drop_all()


@pytest.fixture(params=[
    lazy_fixture("client_minio"),
    lazy_fixture("client_local")
])
def client(request):
    return request.param


@pytest.fixture
def drs_object():
    drs_object = DrsObject(location=DUMMY_FILE)

    db.session.add(drs_object)
    db.session.commit()

    yield drs_object


@pytest.fixture
def drs_bundle():
    bundle = create_drs_bundle(DUMMY_DIRECTORY)

    db.session.commit()

    yield bundle


@pytest.fixture
def drs_object_minio():
    drs_object = DrsObject(location=DUMMY_FILE)

    db.session.add(drs_object)
    db.session.commit()

    yield drs_object


@pytest.fixture
def drs_bundle_minio():
    with mock_s3():
        bundle = create_drs_bundle(DUMMY_DIRECTORY)

        db.session.commit()

        yield bundle
