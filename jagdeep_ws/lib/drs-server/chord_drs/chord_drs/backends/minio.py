import boto3
from flask import current_app
from urllib.parse import urlparse
from chord_drs.backends.base import Backend


__all__ = ["MinioBackend"]


class MinioBackend(Backend):
    def __init__(self, resource=None):
        self.minio = resource or boto3.resource(
            's3',
            endpoint_url=current_app.config["MINIO_URL"],
            aws_access_key_id=current_app.config["MINIO_USERNAME"],
            aws_secret_access_key=current_app.config["MINIO_PASSWORD"]
        )

        self.bucket = self.minio.Bucket(current_app.config["MINIO_BUCKET"])

    @staticmethod
    def build_minio_location(obj):
        host = urlparse(current_app.config["MINIO_URL"]).netloc
        return f"s3://{host}/{obj.bucket_name}/{obj.key}"

    def get_minio_object(self, location: str):
        obj = self.bucket.Object(location.split("/")[-1])
        return obj.get()

    def save(self, current_location: str, filename: str) -> str:
        with open(current_location, "rb") as f:
            obj = self.bucket.put_object(Key=filename, Body=f)
            return MinioBackend.build_minio_location(obj)
