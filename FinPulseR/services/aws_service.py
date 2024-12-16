import boto3
from botocore.exceptions import BotoCoreError, ClientError
from io import BytesIO


class S3Uploader:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str, bucket_name: str):
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    def upload_bytesio(self, file_buffer: BytesIO, file_name: str, s3_key_prefix: str = "uploads/") -> str:
        try:
            s3_key = f"{s3_key_prefix}{file_name}"

            # Upload the file to S3 with public-read ACL
            self.s3_client.upload_fileobj(
                file_buffer,
                self.bucket_name,
                s3_key
            )

            download_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"

            return download_url
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Failed to upload file to S3: {e}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")
