from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.services.storage_service import StorageService
from app.services.mux_service import MuxService
from app.models.user import User
from app.models.flourish import FlourishPost
from pydantic import BaseModel
router = APIRouter()
class VideoUploadReponse(BaseModel):
    post_id: str
    video_url: str
    status: str
@router.post("/upload", response_model=VideoUploadReponse)
async def upload_video(
    file: UploadFile = File(...),
    caption: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    """
    Upload video file
    Max size: 100MB, Duration: 60
    """

    # Validate file type
    if not file.content_type.startswith("video/"):
        raise HTTPException(400, "File must be a video")

    # Read file
    file_data = await file.read()

    # Check size (100MB max)
    if len(file_data) > 100 * 1024 * 1024:
        raise HTTPException(400, "Video too large (max 100MB)")

    # Upload tp R2
    storage = StorageService()
    video_url = storage.upload_video(file_data, file.filename)

    # Send to Mux for encoding
    mux_service = MuxService()
    mux_data = mux_service.create_asset(video_url)

    # Create post in database
    post = FlourishPost(
        author_id=current_user.id,
        content=caption,
        video_url=video_url,
        mux_assest_id=mux_data['asset_id'],
        mux_playback_id=mux_data['playback_id'],
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return {
        "post_id": str(post.id),
        "video_url": video_url,
        "status": "processing"
    }

@router.get("/feed")
def get_video_feed(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get video feed (chronological for now)"""
    posts = db.query(FlourishPost).filter(
        FlourishPost.expires_at > datetime.utcnow(),
        FlourishPost.soft_deleted == False,
        FlourishPost.video_url.isnot(None)
    ).order_by(
        FlourishPost.created_at.desc()
    ).offset(skip).limit(limit).all()

    return {
        "posts": [
            {
                "id": str(p.id),
                "author_id": str(p.author_id),
                "content": p.content,
                "mux_playback_id": p.mux_playback_id,
                "view_count": p.view_count,
                "created_at": p.created_at.isoformat()
                }
                for p in posts
            ]
    }
