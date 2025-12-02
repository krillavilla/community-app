# 🌱 Week 1: Foundation Setup Guide

## Overview
This week focuses on database schema updates, GDPR compliance, and setting up external services (Cloudflare R2, Mux).

**Time Estimate: 8-12 hours**

---

## ✅ Step 0: Complete Onboarding (30 minutes)

Follow `ONBOARDING_SETUP_GUIDE.md` in the root directory to finish the onboarding flow.

---

## 📊 Step 1: Database Schema Migrations (2 hours)

### 1.1 Create Migration File

**File**: `backend/alembic/versions/add_video_features.py`

```python
"""Add video and expiration features

Revision ID: add_video_features
Revises: [previous_revision_id]
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_video_features'
down_revision = '[REPLACE_WITH_LATEST_REVISION]'  # TODO: Update this
branch_labels = None
depends_on = None


def upgrade():
    # Posts table updates
    op.add_column('posts', sa.Column('video_url', sa.String(512), nullable=True))
    op.add_column('posts', sa.Column('thumbnail_url', sa.String(512), nullable=True))
    op.add_column('posts', sa.Column('duration_seconds', sa.Integer(), nullable=True))
    op.add_column('posts', sa.Column('expires_at', sa.DateTime(), nullable=True))
    op.add_column('posts', sa.Column('privacy_level', sa.String(50), nullable=True, server_default='public'))
    op.add_column('posts', sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('posts', sa.Column('screenshot_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('posts', sa.Column('soft_deleted', sa.Boolean(), nullable=False, server_default='false'))
    
    # Create post_views table
    op.create_table(
        'post_views',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('viewer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('watched_duration_seconds', sa.Integer(), nullable=False),
        sa.Column('completion_rate', sa.Float(), nullable=False),
        sa.Column('viewed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_screenshot', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.create_index('idx_post_views_post_id', 'post_views', ['post_id'])
    op.create_index('idx_post_views_viewer_id', 'post_views', ['viewer_id'])
    
    # Comments table updates
    op.add_column('comments', sa.Column('expires_at', sa.DateTime(), nullable=True))
    op.add_column('comments', sa.Column('upvotes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('comments', sa.Column('downvotes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('comments', sa.Column('soft_deleted', sa.Boolean(), nullable=False, server_default='false'))
    
    # Create comment_votes table
    op.create_table(
        'comment_votes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('comment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('comments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vote_type', sa.String(10), nullable=False),  # 'up' or 'down'
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_unique_constraint('uq_comment_vote_user', 'comment_votes', ['comment_id', 'user_id'])
    op.create_index('idx_comment_votes_comment_id', 'comment_votes', ['comment_id'])
    
    # Create privacy_circles table
    op.create_table(
        'privacy_circles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('circle_name', sa.String(100), nullable=False),  # 'friends', 'close_friends', 'orchard'
        sa.Column('member_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_unique_constraint('uq_circle_member', 'privacy_circles', ['user_id', 'circle_name', 'member_id'])
    op.create_index('idx_privacy_circles_user_id', 'privacy_circles', ['user_id'])
    
    # Create direct_messages table
    op.create_table(
        'direct_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recipient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('soft_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_dm_sender_id', 'direct_messages', ['sender_id'])
    op.create_index('idx_dm_recipient_id', 'direct_messages', ['recipient_id'])
    
    # Users table updates for age verification
    op.add_column('users', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('age_verified', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    # Drop new tables
    op.drop_table('direct_messages')
    op.drop_table('privacy_circles')
    op.drop_table('comment_votes')
    op.drop_table('post_views')
    
    # Remove columns from posts
    op.drop_column('posts', 'soft_deleted')
    op.drop_column('posts', 'screenshot_count')
    op.drop_column('posts', 'view_count')
    op.drop_column('posts', 'privacy_level')
    op.drop_column('posts', 'expires_at')
    op.drop_column('posts', 'duration_seconds')
    op.drop_column('posts', 'thumbnail_url')
    op.drop_column('posts', 'video_url')
    
    # Remove columns from comments
    op.drop_column('comments', 'soft_deleted')
    op.drop_column('comments', 'downvotes')
    op.drop_column('comments', 'upvotes')
    op.drop_column('comments', 'expires_at')
    
    # Remove columns from users
    op.drop_column('users', 'age_verified')
    op.drop_column('users', 'date_of_birth')
```

### 1.2 Run Migration

```bash
cd /home/krillavilla/Documents/community-app/backend

# Check current migrations
alembic current

# Update the down_revision in the migration file with the output from above

# Run migration
alembic upgrade head

# Verify
docker compose exec backend alembic current
```

---

## 🔐 Step 2: GDPR Endpoints (2 hours)

### 2.1 Create GDPR Service

**File**: `backend/app/services/gdpr_service.py`

```python
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.habit import Habit
import json
from datetime import datetime

class GDPRService:
    """Handle GDPR data export and deletion requests"""
    
    @staticmethod
    def export_user_data(user_id: str, db: Session) -> dict:
        """Export all user data in JSON format"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Gather all user data
        posts = db.query(Post).filter(Post.author_id == user_id).all()
        comments = db.query(Comment).filter(Comment.author_id == user_id).all()
        habits = db.query(Habit).filter(Habit.user_id == user_id).all()
        
        export_data = {
            "user_profile": {
                "id": str(user.id),
                "email": user.email,
                "display_name": user.display_name,
                "bio": user.bio,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "posts": [
                {
                    "id": str(post.id),
                    "content": post.content,
                    "video_url": post.video_url,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "view_count": post.view_count,
                }
                for post in posts
            ],
            "comments": [
                {
                    "id": str(comment.id),
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat() if comment.created_at else None,
                }
                for comment in comments
            ],
            "habits": [
                {
                    "id": str(habit.id),
                    "name": habit.name,
                    "frequency": habit.frequency,
                    "created_at": habit.created_at.isoformat() if habit.created_at else None,
                }
                for habit in habits
            ],
            "export_timestamp": datetime.utcnow().isoformat(),
        }
        
        return export_data
    
    @staticmethod
    def delete_user_data(user_id: str, db: Session) -> bool:
        """Permanently delete all user data (GDPR Right to be Forgotten)"""
        try:
            # Soft delete posts, comments, habits
            db.query(Post).filter(Post.author_id == user_id).update({"soft_deleted": True})
            db.query(Comment).filter(Comment.author_id == user_id).update({"soft_deleted": True})
            
            # Hard delete habits
            db.query(Habit).filter(Habit.user_id == user_id).delete()
            
            # Mark user as deleted
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.email = f"deleted_{user_id}@deleted.local"
                user.display_name = "Deleted User"
                user.bio = None
                user.soft_deleted = True
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error deleting user data: {e}")
            return False
```

### 2.2 Add GDPR Endpoints

**File**: `backend/app/api/v1/endpoints/gdpr.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.services.gdpr_service import GDPRService
from app.models.user import User
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/export")
def export_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data (GDPR Article 20 - Right to Data Portability)
    """
    data = GDPRService.export_user_data(str(current_user.id), db)
    
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return JSONResponse(content=data)

@router.delete("/delete-account")
def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete all user data (GDPR Article 17 - Right to be Forgotten)
    WARNING: This action is irreversible!
    """
    success = GDPRService.delete_user_data(str(current_user.id), db)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete account")
    
    return {"message": "Account deleted successfully"}
```

### 2.3 Register GDPR Routes

**File**: `backend/app/api/v1/api.py`

Add this import and route:

```python
from app.api.v1.endpoints import gdpr

# Add to api_router
api_router.include_router(gdpr.router, prefix="/gdpr", tags=["gdpr"])
```

---

## 🎥 Step 3: Setup External Services (1 hour)

### 3.1 Sign Up for Cloudflare R2

1. Go to https://dash.cloudflare.com
2. Navigate to R2 Object Storage
3. Create a new bucket: `garden-videos-prod`
4. Generate API credentials:
   - Access Key ID
   - Secret Access Key
   - Endpoint URL

### 3.2 Sign Up for Mux

1. Go to https://mux.com
2. Create account
3. Get API credentials from Settings → Access Tokens
4. Copy:
   - Token ID
   - Token Secret

### 3.3 Update Environment Variables

**File**: `backend/.env`

Add these lines:

```bash
# Cloudflare R2
R2_ACCESS_KEY_ID=your_access_key_here
R2_SECRET_ACCESS_KEY=your_secret_key_here
R2_ENDPOINT_URL=https://your_account_id.r2.cloudflarestorage.com
R2_BUCKET_NAME=garden-videos-prod
R2_PUBLIC_URL=https://your_bucket.r2.dev

# Mux Video
MUX_TOKEN_ID=your_token_id_here
MUX_TOKEN_SECRET=your_token_secret_here

# Content Moderation (optional for now)
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_AI_TOKEN=
```

---

## 🛡️ Step 4: Age Verification Flow (2 hours)

### 4.1 Update User Model

**File**: `backend/app/models/user.py`

Add these fields (already in migration):

```python
from datetime import date, datetime

class User(Base):
    # ... existing fields ...
    date_of_birth = Column(Date, nullable=True)
    age_verified = Column(Boolean, default=False, nullable=False)
    
    @property
    def age(self):
        """Calculate user's current age"""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_minor(self):
        """Check if user is under 18"""
        return self.age and self.age < 18
```

### 4.2 Create Age Verification Endpoint

**File**: `backend/app/api/v1/endpoints/users.py`

Add this endpoint:

```python
from datetime import date
from pydantic import BaseModel

class AgeVerificationRequest(BaseModel):
    date_of_birth: str  # YYYY-MM-DD format

@router.post("/me/verify-age")
def verify_age(
    age_data: AgeVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify user's age (required before posting content)"""
    try:
        dob = date.fromisoformat(age_data.date_of_birth)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Calculate age
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    if age < 13:
        raise HTTPException(status_code=403, detail="You must be at least 13 years old to use Garden")
    
    # Update user
    current_user.date_of_birth = dob
    current_user.age_verified = True
    db.commit()
    
    return {
        "message": "Age verified successfully",
        "is_minor": age < 18
    }
```

---

## 🧪 Step 5: Test Everything (1 hour)

### 5.1 Test Database Migration

```bash
cd /home/krillavilla/Documents/community-app

# Check backend logs
docker compose logs backend --tail=50

# Verify tables exist
docker compose exec postgres psql -U garden_user -d garden_db -c "\dt"

# Should see: post_views, comment_votes, privacy_circles, direct_messages
```

### 5.2 Test GDPR Endpoints

```bash
# Get your Auth0 token from browser (after logging in)
TOKEN="your_auth0_token_here"

# Test export
curl -X GET http://localhost:8000/api/v1/gdpr/export \
  -H "Authorization: Bearer $TOKEN"

# Should return JSON with your user data
```

### 5.3 Test Age Verification

```bash
# Test age verification
curl -X POST http://localhost:8000/api/v1/users/me/verify-age \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date_of_birth": "1990-01-01"}'

# Should return: {"message": "Age verified successfully", "is_minor": false}
```

---

## ✅ Week 1 Checklist

- [ ] Onboarding flow completed
- [ ] Database migration created and run
- [ ] GDPR service implemented
- [ ] GDPR endpoints working
- [ ] Cloudflare R2 account created
- [ ] Mux account created
- [ ] Environment variables updated
- [ ] Age verification implemented
- [ ] All tests passing

---

## 🚀 Next Steps

Once Week 1 is complete, move to **Week 2-3: Video Core** (guide coming next).

You'll build:
- Video upload endpoint
- R2 storage integration
- Mux transcoding
- Video player component
- Swipeable feed UI
