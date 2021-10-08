from hashlib import sha256


__all__ = ["drs_file_checksum"]


def drs_file_checksum(path: str) -> str:
    hash_obj = sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()
