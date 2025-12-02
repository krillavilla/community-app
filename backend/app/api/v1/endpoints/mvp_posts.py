"""
MVP Posts API - Simplified video social features.

Endpoints:
- POST /posts - Upload video/post
- GET /feed - Chronological feed
- POST /posts/{id}/like - Like/unlike
- POST /posts/{id}/view - Track view
- GET /posts/{id}/comments - Get comments
- POST /posts/{id}/comments - Add comment
- POST /comments/{id}/vote - Vote on comment
- POST /users/{id}/follow - Follow/unfollow user
- GET /users/{id}/profile - Get user profile
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Optional
import uuid

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.user import User
from app.models.mvp import Post, MvpComment, Like, CommentVote, Follow
from app.services.r2_storage import R2StorageService
from pydantic import BaseModel

router = APIRouter()


# ===== SCHEMAS =====

class PostResponse(BaseModel):
    id: str
    author_id: str
    author_name: str
    caption: Optional[str]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    view_count: int
    like_count: int
    comment_count: int
    hours_remaining: float
    is_liked: bool
    created_at: str
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    id: str
    author_id: str
    author_name: str
    content: str
    upvote_count: int
    downvote_count: int
    net_votes: int
    user_vote: Optional[str]  # 'up', 'down', or None
    created_at: str
    
    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    id: str
    display_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    post_count: int
    follower_count: int
    following_count: int
    is_following: bool
    
    class Config:
        from_attributes = True


# ===== POST ENDPOINTS =====

@router.post("/posts")
async def create_post(
    caption: str = Form(""),
    is_public: bool = Form(True),
    video_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new post (text or video).
    
    For MVP: No video processing yet (TODO: add R2 upload).
    Post expires in 24 hours.
    """
    # Upload video to R2 storage
    video_url = None
    if video_file:
        # Read file data
        file_data = await video_file.read()
        
        # Validate file size (100MB max for MVP)
        max_size = 100 * 1024 * 1024  # 100MB
        if len(file_data) > max_size:
            raise HTTPException(400, "Video too large (max 100MB)")
        
        # Upload to R2
        storage = R2StorageService()
        video_url = storage.upload_video(file_data, video_file.filename, video_file.content_type)
    
    # Create post with 24hr expiration
    post = Post(
        id=uuid.uuid4(),
        author_id=current_user.id,
        caption=caption,
        video_url=video_url,
        is_public=is_public,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return {
        "id": str(post.id),
        "message": "Post created! Expires in 24 hours.",
        "expires_at": post.expires_at.isoformat()
    }


@router.get("/feed")
def get_feed(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chronological feed of posts.
    
    Simple MVP feed:
    - Shows public posts + friends' posts
    - Sorted by created_at DESC (most recent first)
    - Excludes expired/deleted posts
    """
    # Get list of users current_user follows
    following_ids = db.query(Follow.following_id).filter(
        Follow.follower_id == current_user.id
    ).subquery()
    
    # Query posts: public OR from people I follow
    posts_query = db.query(Post).filter(
        and_(
            Post.soft_deleted == False,
            Post.expires_at > datetime.utcnow(),
            or_(
                Post.is_public == True,
                Post.author_id.in_(following_ids)
            )
        )
    ).order_by(Post.created_at.desc())
    
    posts = posts_query.offset(skip).limit(limit).all()
    
    # Check which posts current user has liked
    liked_post_ids = set()
    if posts:
        post_ids = [p.id for p in posts]
        likes = db.query(Like.post_id).filter(
            and_(
                Like.post_id.in_(post_ids),
                Like.user_id == current_user.id
            )
        ).all()
        liked_post_ids = {like[0] for like in likes}
    
    # Build response
    response = []
    for post in posts:
        response.append({
            "id": str(post.id),
            "author_id": str(post.author_id),
            "author_name": post.author.display_name,
            "caption": post.caption,
            "video_url": post.video_url,
            "thumbnail_url": post.thumbnail_url,
            "view_count": post.view_count,
            "like_count": post.like_count,
            "comment_count": post.comment_count,
            "hours_remaining": post.hours_remaining,
            "is_liked": post.id in liked_post_ids,
            "created_at": post.created_at.isoformat()
        })
    
    return {
        "posts": response,
        "total": len(response)
    }


@router.post("/posts/{post_id}/like")
def toggle_like(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Like or unlike a post.
    
    Symbolic "watering" in Garden metaphor.
    """
    post = db.query(Post).filter(Post.id == uuid.UUID(post_id)).first()
    if not post:
        raise HTTPException(404, "Post not found")
    
    # Check if already liked
    existing_like = db.query(Like).filter(
        and_(
            Like.post_id == post.id,
            Like.user_id == current_user.id
        )
    ).first()
    
    if existing_like:
        # Unlike
        db.delete(existing_like)
        post.like_count = max(0, post.like_count - 1)
        action = "unliked"
    else:
        # Like
        like = Like(
            id=uuid.uuid4(),
            post_id=post.id,
            user_id=current_user.id
        )
        db.add(like)
        post.like_count += 1
        action = "liked"
    
    db.commit()
    
    return {
        "action": action,
        "like_count": post.like_count
    }


@router.post("/posts/{post_id}/view")
def track_view(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track a view on a post."""
    post = db.query(Post).filter(Post.id == uuid.UUID(post_id)).first()
    if not post:
        raise HTTPException(404, "Post not found")
    
    post.view_count += 1
    db.commit()
    
    return {"view_count": post.view_count}


# ===== COMMENT ENDPOINTS =====

@router.get("/posts/{post_id}/comments")
def get_comments(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments for a post (symbolic "soil")."""
    post = db.query(Post).filter(Post.id == uuid.UUID(post_id)).first()
    if not post:
        raise HTTPException(404, "Post not found")
    
    # Get active comments
    comments = db.query(MvpComment).filter(
        and_(
            MvpComment.post_id == post.id,
            MvpComment.soft_deleted == False,
            MvpComment.expires_at > datetime.utcnow()
        )
    ).order_by(MvpComment.created_at.desc()).all()
    
    # Get user's votes
    if comments:
        comment_ids = [c.id for c in comments]
        user_votes = db.query(CommentVote).filter(
            and_(
                CommentVote.comment_id.in_(comment_ids),
                CommentVote.user_id == current_user.id
            )
        ).all()
        vote_map = {v.comment_id: v.vote_type for v in user_votes}
    else:
        vote_map = {}
    
    response = []
    for comment in comments:
        response.append({
            "id": str(comment.id),
            "author_id": str(comment.author_id),
            "author_name": comment.author.display_name,
            "content": comment.content,
            "upvote_count": comment.upvote_count,
            "downvote_count": comment.downvote_count,
            "net_votes": comment.net_votes,
            "user_vote": vote_map.get(comment.id),
            "created_at": comment.created_at.isoformat()
        })
    
    return {"comments": response}


@router.post("/posts/{post_id}/comments")
def add_comment(
    post_id: str,
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add comment to a post."""
    post = db.query(Post).filter(Post.id == uuid.UUID(post_id)).first()
    if not post:
        raise HTTPException(404, "Post not found")
    
    if post.is_expired:
        raise HTTPException(400, "Cannot comment on expired post")
    
    # Create comment with 7-day expiration
    comment = MvpComment(
        id=uuid.uuid4(),
        post_id=post.id,
        author_id=current_user.id,
        content=content,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    db.add(comment)
    post.comment_count += 1
    db.commit()
    db.refresh(comment)
    
    return {
        "id": str(comment.id),
        "message": "Comment added! Expires in 7 days."
    }


@router.post("/comments/{comment_id}/vote")
def vote_comment(
    comment_id: str,
    vote_type: str = Form(...),  # 'up', 'down', or 'remove'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vote on a comment (upvote/downvote).
    
    vote_type: 'up', 'down', or 'remove'
    """
    if vote_type not in ['up', 'down', 'remove']:
        raise HTTPException(400, "Invalid vote_type. Use 'up', 'down', or 'remove'")
    
    comment = db.query(MvpComment).filter(MvpComment.id == uuid.UUID(comment_id)).first()
    if not comment:
        raise HTTPException(404, "Comment not found")
    
    # Check existing vote
    existing_vote = db.query(CommentVote).filter(
        and_(
            CommentVote.comment_id == comment.id,
            CommentVote.user_id == current_user.id
        )
    ).first()
    
    if vote_type == 'remove':
        if existing_vote:
            # Remove vote
            if existing_vote.vote_type == 'up':
                comment.upvote_count = max(0, comment.upvote_count - 1)
            else:
                comment.downvote_count = max(0, comment.downvote_count - 1)
            db.delete(existing_vote)
            action = "removed"
        else:
            action = "no_vote_to_remove"
    else:
        if existing_vote:
            # Change vote
            if existing_vote.vote_type != vote_type:
                # Switch from up to down or vice versa
                if existing_vote.vote_type == 'up':
                    comment.upvote_count = max(0, comment.upvote_count - 1)
                    comment.downvote_count += 1
                else:
                    comment.downvote_count = max(0, comment.downvote_count - 1)
                    comment.upvote_count += 1
                existing_vote.vote_type = vote_type
                action = f"changed_to_{vote_type}"
            else:
                action = f"already_{vote_type}voted"
        else:
            # New vote
            vote = CommentVote(
                id=uuid.uuid4(),
                comment_id=comment.id,
                user_id=current_user.id,
                vote_type=vote_type
            )
            db.add(vote)
            if vote_type == 'up':
                comment.upvote_count += 1
            else:
                comment.downvote_count += 1
            action = f"{vote_type}voted"
    
    db.commit()
    
    return {
        "action": action,
        "upvote_count": comment.upvote_count,
        "downvote_count": comment.downvote_count,
        "net_votes": comment.net_votes
    }


# ===== FOLLOW ENDPOINTS =====

@router.post("/users/{user_id}/follow")
def toggle_follow(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Follow or unfollow a user."""
    target_user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not target_user:
        raise HTTPException(404, "User not found")
    
    if target_user.id == current_user.id:
        raise HTTPException(400, "Cannot follow yourself")
    
    # Check if already following
    existing_follow = db.query(Follow).filter(
        and_(
            Follow.follower_id == current_user.id,
            Follow.following_id == target_user.id
        )
    ).first()
    
    if existing_follow:
        # Unfollow
        db.delete(existing_follow)
        action = "unfollowed"
    else:
        # Follow
        follow = Follow(
            id=uuid.uuid4(),
            follower_id=current_user.id,
            following_id=target_user.id
        )
        db.add(follow)
        action = "followed"
    
    db.commit()
    
    return {"action": action}


# ===== PROFILE ENDPOINTS =====

@router.get("/users/{user_id}/profile")
def get_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile with stats."""
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Count posts
    post_count = db.query(func.count(Post.id)).filter(
        and_(
            Post.author_id == user.id,
            Post.soft_deleted == False
        )
    ).scalar()
    
    # Count followers
    follower_count = db.query(func.count(Follow.id)).filter(
        Follow.following_id == user.id
    ).scalar()
    
    # Count following
    following_count = db.query(func.count(Follow.id)).filter(
        Follow.follower_id == user.id
    ).scalar()
    
    # Check if current user follows this user
    is_following = db.query(Follow).filter(
        and_(
            Follow.follower_id == current_user.id,
            Follow.following_id == user.id
        )
    ).first() is not None
    
    return {
        "id": str(user.id),
        "display_name": user.display_name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "post_count": post_count,
        "follower_count": follower_count,
        "following_count": following_count,
        "is_following": is_following
    }


@router.get("/users/{user_id}/posts")
def get_user_posts(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get posts by a specific user."""
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Check if can view posts (public or following)
    is_following = db.query(Follow).filter(
        and_(
            Follow.follower_id == current_user.id,
            Follow.following_id == user.id
        )
    ).first() is not None
    
    # Query posts
    posts_query = db.query(Post).filter(
        and_(
            Post.author_id == user.id,
            Post.soft_deleted == False,
            Post.expires_at > datetime.utcnow(),
            or_(
                Post.is_public == True,
                current_user.id == user.id,  # Own posts
                is_following  # Following user
            )
        )
    ).order_by(Post.created_at.desc())
    
    posts = posts_query.offset(skip).limit(limit).all()
    
    # Check which posts current user has liked
    liked_post_ids = set()
    if posts:
        post_ids = [p.id for p in posts]
        likes = db.query(Like.post_id).filter(
            and_(
                Like.post_id.in_(post_ids),
                Like.user_id == current_user.id
            )
        ).all()
        liked_post_ids = {like[0] for like in likes}
    
    # Build response
    response = []
    for post in posts:
        response.append({
            "id": str(post.id),
            "caption": post.caption,
            "video_url": post.video_url,
            "thumbnail_url": post.thumbnail_url,
            "view_count": post.view_count,
            "like_count": post.like_count,
            "comment_count": post.comment_count,
            "hours_remaining": post.hours_remaining,
            "is_liked": post.id in liked_post_ids,
            "created_at": post.created_at.isoformat()
        })
    
    return {
        "user": {
            "id": str(user.id),
            "display_name": user.display_name
        },
        "posts": response
    }
