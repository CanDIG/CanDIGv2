import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from chord_drs.constants import SERVICE_NAME, SERVICE_TYPE
from chord_drs.data_sources import DATA_SOURCE_LOCAL, DATA_SOURCE_MINIO


__all__ = [
    "APP_DIR",
    "BASEDIR",
    "Config",
]


load_dotenv()


APP_DIR = Path(__file__).resolve().parents[0]

# when deployed inside chord_singularity, DATABASE will be set
BASEDIR = os.environ.get("DATABASE", APP_DIR.parent)
SERVICE_DATA = Path(os.environ.get("DATA", os.path.join(Path.home(), "chord_drs_data"))).expanduser().resolve()

# MinIO-related, check if the credentials have been provided in a file
MINIO_URL = os.environ.get("MINIO_URL")
MINIO_ACCESS_KEY_FILE = os.environ.get("MINIO_ACCESS_KEY_FILE")
MINIO_SECRET_KEY_FILE = os.environ.get("MINIO_ACCESS_KEY_FILE")

MINIO_USERNAME = os.environ.get("MINIO_USERNAME")
MINIO_PASSWORD = os.environ.get("MINIO_PASSWORD")

if MINIO_SECRET_KEY_FILE:
    MINIO_ACCESS_KEY_PATH = Path(MINIO_ACCESS_KEY_FILE).resolve()

    if MINIO_ACCESS_KEY_PATH.exists():
        with open(MINIO_ACCESS_KEY_PATH, "r") as f:
            MINIO_USERNAME = f.read().strip()

if MINIO_SECRET_KEY_FILE:
    MINIO_SECRET_KEY_PATH = Path(MINIO_SECRET_KEY_FILE).resolve()
    if MINIO_SECRET_KEY_PATH.exists():
        with open(MINIO_SECRET_KEY_PATH, "r") as f:
            MINIO_PASSWORD = f.read().strip()


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(Path(os.path.join(BASEDIR, "db.sqlite3")).expanduser().resolve())
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CHORD_URL: Optional[str] = os.environ.get("CHORD_URL")
    CHORD_SERVICE_URL_BASE_PATH: Optional[str] = os.environ.get("SERVICE_URL_BASE_PATH")
    SERVICE_ID: str = os.environ.get("SERVICE_ID", SERVICE_TYPE)
    SERVICE_DATA_SOURCE: str = DATA_SOURCE_MINIO if MINIO_URL else DATA_SOURCE_LOCAL
    SERVICE_DATA: Optional[str] = None if MINIO_URL else SERVICE_DATA
    MINIO_URL: Optional[str] = MINIO_URL
    MINIO_USERNAME: Optional[str] = MINIO_USERNAME
    MINIO_PASSWORD: Optional[str] = MINIO_PASSWORD
    MINIO_BUCKET: Optional[str] = os.environ.get("MINIO_BUCKET") if MINIO_URL else None


print(f"[{SERVICE_NAME}] Using: database URI {Config.SQLALCHEMY_DATABASE_URI}")
print(f"[{SERVICE_NAME}]         data source {Config.SERVICE_DATA_SOURCE}")
print(f"[{SERVICE_NAME}]           data path {Config.SERVICE_DATA}")
print(f"[{SERVICE_NAME}]           minio url {Config.MINIO_URL}", flush=True)
