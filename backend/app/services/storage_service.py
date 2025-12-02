import boto3
from botocore.client import Config
from app.core.config import settings
import uuid
from datetime import datetime
class StorageService:
	
	def __init__(self):
		self.s3_client = boto3.client(
			's3',
			endpoint_url=settings.R2_ENDPOINT_URL,
			aws_access_key_id=settings.R2_ACCESS_KEY_ID,
			aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
			config=Config(signature_version='s3v4'),
		)
		self.bucket = settings.R2_BUCKET_NAME

	def upload_video(self, file_data: bytes, filename: str) -> str:
		"""Upload video to R2, return public URL"""
		# Generate unique filename
		ext = filename.split(',')[-1]
		unique_name = f'videos/{uuid.uuid4()}.{ext}'

		# Upload to R2
		self.s3_client.put_object(
			Bucket=self.bucket,
			Key=unique_name,
			Body=file_data,
			ContentType=f'video/{ext}'
		)

		# Return public URL
		return f"{settings.R2_PUBLIC_URL}/{unique_name}"

	def delete_video(self, video_key: str):
		"""Delete video from R2"""
		self.s3_client.delete_object(
			Bucket=self.bucket,
			Key=video_key,
		)
