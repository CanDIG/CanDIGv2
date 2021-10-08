__all__ = ["make_resource_id"]


def make_resource_id(namespace_prefix: str, version: str = "") -> str:
    namespace_prefix = namespace_prefix.strip()
    version = version.strip()
    return namespace_prefix if not version else f"{namespace_prefix}:{version}"
