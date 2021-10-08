from typing import Dict, Type

from chord_drs.backends.base import Backend
from chord_drs.backends.local import LocalBackend
from chord_drs.backends.minio import MinioBackend


__all__ = [
    "DATA_SOURCE_LOCAL",
    "DATA_SOURCE_MINIO",
    "DATA_SOURCE_BACKENDS",
]


DATA_SOURCE_LOCAL = "local"
DATA_SOURCE_MINIO = "minio"

DATA_SOURCE_BACKENDS: Dict[str, Type[Backend]] = {
    DATA_SOURCE_LOCAL: LocalBackend,
    DATA_SOURCE_MINIO: MinioBackend,
}
