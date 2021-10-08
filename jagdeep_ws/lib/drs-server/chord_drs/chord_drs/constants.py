from chord_drs import __version__

__all__ = ["SERVICE_NAME", "SERVICE_ARTIFACT", "SERVICE_TYPE"]

SERVICE_NAME = "CHORD Data Repository Service"
SERVICE_ARTIFACT = "drs"
SERVICE_TYPE = f"ca.c3g.chord:{SERVICE_ARTIFACT}:{__version__}"
