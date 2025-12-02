# 🎥 Week 2-3: Video Platform Implementation Guide

## Overview
Build video upload, player, swipeable feed, and comment voting system.

**Time Estimate**: 16-24 hours over 2-3 weeks

---

## Prerequisites

✅ Week 1 complete (onboarding, GDPR, database)  
✅ Cloudflare R2 account + credentials  
✅ Mux account + API tokens  
✅ Credentials in `backend/.env`

---

## Architecture Summary

```
User uploads video → Backend receives file → Upload to R2 → 
Send to Mux for encoding → Store metadata in DB → 
User can view in swipeable feed → Add comments with votes
```

---

## Part 1: Backend - Video Upload (4-6 hours)

### 1.1 Install Dependencies

**File**: `backend/requirements.txt`

Add these lines:
```
boto3==1.34.0  # AWS SDK (works with R2)
mux-python==0.18.0  # Mux SDK
python-multipart==0.0.6  # File uploads
```

Rebuild:
```bash
docker compose build backend
docker compose restart backend
```

### 1.2 Create R2 Storage Service

**File**: `backend/app/services/storage_service.py`

```python
import boto3
from botocore.client import Config
from app.core.config import settings
import uuid
from datetime import datetime

class StorageService:
    """Handle video uploads to Cloudflare R2"""
    
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
        ext = filename.split('.')[-1]
        unique_name = f"videos/{uuid.uuid4()}.{ext}"
        
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
            Key=video_key
        )
```

### 1.3 Create Mux Service

**File**: `backend/app/services/mux_service.py`

```python
import mux_python
from app.core.config import settings

class MuxService:
    """Handle video encoding with Mux"""
    
    def __init__(self):
        configuration = mux_python.Configuration()
        configuration.username = settings.MUX_TOKEN_ID
        configuration.password = settings.MUX_TOKEN_SECRET
        
        self.assets_api = mux_python.AssetsApi(
            mux_python.ApiClient(configuration)
        )
    
    def create_asset(self, video_url: str) -> dict:
        """Create Mux asset from video URL"""
        create_asset_request = mux_python.CreateAssetRequest(
            input=[mux_python.InputSettings(url=video_url)],
            playback_policy=[mux_python.PlaybackPolicy.PUBLIC]
        )
        
        asset = self.assets_api.create_asset(create_asset_request)
        
        return {
            'asset_id': asset.data.id,
            'playback_id': asset.data.playback_ids[0].id if asset.data.playback_ids else None,
            'status': asset.data.status
        }
    
    def get_asset_status(self, asset_id: str) -> str:
        """Check encoding status"""
        asset = self.assets_api.get_asset(asset_id)
        return asset.data.status  # 'preparing', 'ready', 'errored'
```

### 1.4 Update Config

**File**: `backend/app/core/config.py`

Add to `Settings` class:
```python
# R2 Storage
R2_ACCESS_KEY_ID: str = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_ENDPOINT_URL: str = os.getenv("R2_ENDPOINT_URL", "")
R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "garden-videos-prod")
R2_PUBLIC_URL: str = os.getenv("R2_PUBLIC_URL", "")

# Mux Video
MUX_TOKEN_ID: str = os.getenv("MUX_TOKEN_ID", "")
MUX_TOKEN_SECRET: str = os.getenv("MUX_TOKEN_SECRET", "")
```

### 1.5 Create Video Upload Endpoint

**File**: `backend/app/api/v1/endpoints/videos.py`

```python
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.services.storage_service import StorageService
from app.services.mux_service import MuxService
from app.models.user import User
from app.models.flourish import FlourishPost
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

class VideoUploadResponse(BaseModel):
    post_id: str
    video_url: str
    status: str

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    caption: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload video file
    Max size: 100MB, Duration: 60 seconds
    """
    # Validate file type
    if not file.content_type.startswith('video/'):
        raise HTTPException(400, "File must be a video")
    
    # Read file
    file_data = await file.read()
    
    # Check size (100MB max)
    if len(file_data) > 100 * 1024 * 1024:
        raise HTTPException(400, "Video too large (max 100MB)")
    
    # Upload to R2
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
        mux_asset_id=mux_data['asset_id'],
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
```

### 1.6 Register Video Routes

**File**: `backend/app/main.py`

Add:
```python
from app.api.v1.endpoints import videos

app.include_router(videos.router, prefix=f"{settings.API_V1_PREFIX}/videos", tags=["videos"])
```

### 1.7 Update FlourishPost Model

**File**: `backend/app/models/flourish.py`

Add columns if missing:
```python
mux_asset_id = Column(String(255), nullable=True)
mux_playback_id = Column(String(255), nullable=True)
```

---

## Part 2: Frontend - Video Upload (3-4 hours)

### 2.1 Install Dependencies

**File**: `frontend/package.json`

Add:
```json
"react-webcam": "^7.2.0"
```

Run:
```bash
cd frontend
npm install
```

### 2.2 Create Video Recorder Component

**File**: `frontend/src/components/video/VideoRecorder.jsx`

```jsx
import { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import { uploadVideo } from '../../services/api';

export default function VideoRecorder({ onUploadComplete }) {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [caption, setCaption] = useState('');
  const [uploading, setUploading] = useState(false);

  const startRecording = () => {
    setRecording(true);
    mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
      mimeType: 'video/webm'
    });
    
    mediaRecorderRef.current.addEventListener('dataavailable', ({ data }) => {
      if (data.size > 0) {
        setRecordedChunks(prev => [...prev, data]);
      }
    });
    
    mediaRecorderRef.current.start();
    
    // Auto-stop after 60 seconds
    setTimeout(() => {
      if (mediaRecorderRef.current?.state === 'recording') {
        stopRecording();
      }
    }, 60000);
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };

  const handleUpload = async () => {
    if (recordedChunks.length === 0) return;
    
    setUploading(true);
    
    const blob = new Blob(recordedChunks, { type: 'video/webm' });
    const formData = new FormData();
    formData.append('file', blob, 'video.webm');
    formData.append('caption', caption);
    
    try {
      const result = await uploadVideo(formData);
      onUploadComplete(result);
    } catch (error) {
      alert('Upload failed: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-4 space-y-4">
      <Webcam
        ref={webcamRef}
        audio={true}
        videoConstraints={{ facingMode: 'user' }}
        className="w-full rounded-lg"
      />
      
      <div className="flex gap-4">
        {!recording ? (
          <button
            onClick={startRecording}
            className="flex-1 bg-red-600 text-white py-3 rounded-full"
          >
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="flex-1 bg-gray-600 text-white py-3 rounded-full"
          >
            Stop (60s max)
          </button>
        )}
      </div>
      
      {recordedChunks.length > 0 && (
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Add a caption..."
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg"
          />
          
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full bg-green-600 text-white py-3 rounded-full disabled:bg-gray-400"
          >
            {uploading ? 'Uploading...' : 'Post Video'}
          </button>
        </div>
      )}
    </div>
  );
}
```

### 2.3 Update API Service

**File**: `frontend/src/services/api.js`

Add:
```javascript
export const uploadVideo = async (formData) => {
  const token = await getToken();
  const response = await fetch(`${API_URL}/videos/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  if (!response.ok) throw new Error('Upload failed');
  return response.json();
};

export const getVideoFeed = async (skip = 0, limit = 10) => {
  const token = await getToken();
  const response = await fetch(
    `${API_URL}/videos/feed?skip=${skip}&limit=${limit}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  return response.json();
};
```

---

## Part 3: Video Player & Feed (4-5 hours)

### 3.1 Install Swiper

```bash
cd frontend
npm install swiper
```

### 3.2 Create Video Player

**File**: `frontend/src/components/video/VideoPlayer.jsx`

```jsx
export default function VideoPlayer({ muxPlaybackId, caption, author }) {
  const videoUrl = `https://stream.mux.com/${muxPlaybackId}.m3u8`;
  
  return (
    <div className="relative h-screen w-full bg-black">
      <video
        src={videoUrl}
        controls
        autoPlay
        loop
        playsInline
        className="h-full w-full object-contain"
      />
      
      <div className="absolute bottom-20 left-0 right-0 p-4 text-white">
        <p className="font-semibold">@{author}</p>
        <p className="mt-2">{caption}</p>
      </div>
    </div>
  );
}
```

### 3.3 Create Swipeable Feed

**File**: `frontend/src/components/feed/SwipeableFeed.jsx`

```jsx
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import VideoPlayer from '../video/VideoPlayer';
import { useEffect, useState } from 'react';
import { getVideoFeed } from '../../services/api';

export default function SwipeableFeed() {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      const data = await getVideoFeed(0, 20);
      setVideos(data.posts);
    } catch (error) {
      console.error('Failed to load videos:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <Swiper
      direction="vertical"
      slidesPerView={1}
      spaceBetween={0}
      mousewheel={true}
      className="h-screen w-full"
    >
      {videos.map((video) => (
        <SwiperSlide key={video.id}>
          <VideoPlayer
            muxPlaybackId={video.mux_playback_id}
            caption={video.content}
            author={video.author_id}
          />
        </SwiperSlide>
      ))}
    </Swiper>
  );
}
```

---

## Part 4: Comment System with Voting (5-6 hours)

### 4.1 Backend - Comment Voting Endpoints

**File**: `backend/app/api/v1/endpoints/comments.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.user import User
from app.models.flourish import Comment
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

class CreateCommentRequest(BaseModel):
    post_id: str
    content: str

@router.post("/")
def create_comment(
    data: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create comment with 7-day expiration"""
    comment = Comment(
        author_id=current_user.id,
        post_id=data.post_id,
        content=data.content,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return {"id": str(comment.id), "expires_at": comment.expires_at}

@router.post("/{comment_id}/vote")
def vote_comment(
    comment_id: str,
    vote_type: str,  # 'up' or 'down'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Vote on comment (extends/reduces lifespan)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(404, "Comment not found")
    
    if vote_type == 'up':
        comment.upvotes += 1
        # Add 6 hours
        comment.expires_at += timedelta(hours=6)
    elif vote_type == 'down':
        comment.downvotes += 1
        # Auto-delete if 5+ downvotes
        if comment.downvotes >= 5:
            comment.soft_deleted = True
    
    db.commit()
    
    return {"upvotes": comment.upvotes, "downvotes": comment.downvotes}
```

### 4.2 Register Comment Routes

**File**: `backend/app/main.py`

```python
from app.api.v1.endpoints import comments

app.include_router(comments.router, prefix=f"{settings.API_V1_PREFIX}/comments", tags=["comments"])
```

### 4.3 Frontend - Comment Component

**File**: `frontend/src/components/comments/CommentSection.jsx`

```jsx
import { useState } from 'react';
import { createComment, voteComment } from '../../services/api';

export default function CommentSection({ postId }) {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

  const handleSubmit = async () => {
    const result = await createComment(postId, newComment);
    setComments([...comments, result]);
    setNewComment('');
  };

  const handleVote = async (commentId, type) => {
    await voteComment(commentId, type);
    // Refresh comments
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add comment..."
          className="flex-1 px-4 py-2 border rounded-full"
        />
        <button
          onClick={handleSubmit}
          className="px-6 py-2 bg-green-600 text-white rounded-full"
        >
          Post
        </button>
      </div>
      
      {comments.map(comment => (
        <div key={comment.id} className="flex justify-between items-center">
          <p>{comment.content}</p>
          <div className="flex gap-2">
            <button onClick={() => handleVote(comment.id, 'up')}>👍</button>
            <button onClick={() => handleVote(comment.id, 'down')}>👎</button>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## Testing & Deployment

### Test Locally

```bash
# Start all services
docker compose up -d

# Test video upload
# Go to http://localhost/upload

# Test feed
# Go to http://localhost/feed
```

### Deploy

Follow DigitalOcean deployment guide after local testing succeeds.

---

## Summary

**Week 2**: Video upload, storage, encoding  
**Week 3**: Player, feed, comments

Total: 16-24 hours spread over 2-3 weeks.
