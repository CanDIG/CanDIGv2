from flask import current_app, g
from typing import Optional

from chord_drs.backends.base import Backend
from chord_drs.data_sources import DATA_SOURCE_BACKENDS


__all__ = [
    "get_backend",
    "close_backend",
]


def _get_backend() -> Optional[Backend]:
    # Instantiate backend if needed
    backend_class = DATA_SOURCE_BACKENDS.get(current_app.config["SERVICE_DATA_SOURCE"])
    return backend_class() if backend_class else None


def get_backend() -> Optional[Backend]:
    if "backend" not in g:
        g.backend = _get_backend()
    return g.backend


def close_backend(_e=None):
    g.pop("backend", None)
