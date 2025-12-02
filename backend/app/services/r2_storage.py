"""
Simple R2 Storage Service for MVP video uploads.

Uses Cloudflare R2 (S3-compatible) for video storage.
No Mux encoding for MVP - direct video storage only.
"""
import os
import uuid
import boto3
from botocore.exceptions import ClientError
from typing import Optional


class R2StorageService:
    """
    Cloudflare R2 storage client.
    
    Environment variables required:
    - R2_ACCESS_KEY_ID
    - R2_SECRET_ACCESS_KEY
    - R2_ENDPOINT_URL
    - R2_BUCKET_NAME (default: garden-videos)
    """
    
    def __init__(self):
        self.access_key_id = os.getenv("R2_ACCESS_KEY_ID")
        self.secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.endpoint_url = os.getenv("R2_ENDPOINT_URL")
        self.bucket_name = os.getenv("R2_BUCKET_NAME", "garden-videos")
        
        # For MVP: Allow running without R2 configured
        self.enabled = bool(self.access_key_id and self.secret_access_key and self.endpoint_url)
        
        if self.enabled:
            # Initialize S3 client (R2 is S3-compatible)
            self.client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name='auto'  # R2 uses 'auto' for region
            )
        else:
            self.client = None
            print("WARNING: R2 not configured. Video uploads will be stored locally (dev mode)")
    
    def upload_video(self, file_data: bytes, filename: str, content_type: str = "video/mp4") -> str:
        """
        Upload video to R2 storage.
        
        Args:
            file_data: Raw video file bytes
            filename: Original filename
            content_type: MIME type
        
        Returns:
            Public URL to the uploaded video
        """
        if not self.enabled:
            # DEV MODE: Save locally for testing
            return self._upload_local(file_data, filename)
        
        # Generate unique filename
        file_extension = filename.split('.')[-1] if '.' in filename else 'mp4'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        object_key = f"videos/{unique_filename}"
        
        try:
            # Upload to R2
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_data,
                ContentType=content_type
            )
            
            # Return public URL
            # R2 public URL format: https://<bucket>.<account>.r2.cloudflarestorage.com/<key>
            public_url = f"{self.endpoint_url}/{self.bucket_name}/{object_key}"
            return public_url
            
        except ClientError as e:
            print(f"Error uploading to R2: {e}")
            # Fallback to local storage
            return self._upload_local(file_data, filename)
    
    def _upload_local(self, file_data: bytes, filename: str) -> str:
        """Fallback: Save video locally for dev/testing."""
        # Create uploads directory if it doesn't exist
        upload_dir = "/tmp/garden_uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = filename.split('.')[-1] if '.' in filename else 'mp4'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        filepath = os.path.join(upload_dir, unique_filename)
        
        # Write file
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        # Return local URL (for dev only)
        return f"file://{filepath}"
    
    def delete_video(self, video_url: str) -> bool:
        """
        Delete video from R2 storage.
        
        Args:
            video_url: Full URL to the video
        
        Returns:
            True if deleted successfully
        """
        if not self.enabled or video_url.startswith("file://"):
            # Local file or R2 not enabled
            if video_url.startswith("file://"):
                filepath = video_url.replace("file://", "")
                try:
                    os.remove(filepath)
                    return True
                except:
                    return False
            return True
        
        try:
            # Extract object key from URL
            object_key = video_url.split(f"{self.bucket_name}/")[-1]
            
            # Delete from R2
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
            
        except ClientError as e:
            print(f"Error deleting from R2: {e}")
            return False
