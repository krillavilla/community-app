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
