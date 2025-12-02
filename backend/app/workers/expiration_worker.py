"""
Simple expiration worker for MVP.

Runs nightly to:
- Soft-delete posts older than 24 hours
- Soft-delete comments older than 7 days

No complex lifecycle logic - just straightforward expiration.
"""
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import and_

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal
from app.models.mvp import Post, MvpComment


def expire_posts():
    """Soft-delete posts that have expired (>24 hours old)."""
    db = SessionLocal()
    try:
        # Find expired posts that aren't already soft-deleted
        expired_posts = db.query(Post).filter(
            and_(
                Post.expires_at < datetime.utcnow(),
                Post.soft_deleted == False
            )
        ).all()
        
        count = 0
        for post in expired_posts:
            post.soft_deleted = True
            count += 1
        
        db.commit()
        print(f"[{datetime.utcnow()}] Expired {count} posts")
        return count
    except Exception as e:
        print(f"Error expiring posts: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def expire_comments():
    """Soft-delete comments that have expired (>7 days old)."""
    db = SessionLocal()
    try:
        # Find expired comments that aren't already soft-deleted
        expired_comments = db.query(MvpComment).filter(
            and_(
                MvpComment.expires_at < datetime.utcnow(),
                MvpComment.soft_deleted == False
            )
        ).all()
        
        count = 0
        for comment in expired_comments:
            comment.soft_deleted = True
            count += 1
        
        db.commit()
        print(f"[{datetime.utcnow()}] Expired {count} comments")
        return count
    except Exception as e:
        print(f"Error expiring comments: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def run_expiration_worker():
    """Main entry point - run all expiration tasks."""
    print(f"\n=== Running expiration worker at {datetime.utcnow()} ===")
    
    try:
        posts_expired = expire_posts()
        comments_expired = expire_comments()
        
        print(f"✓ Completed successfully")
        print(f"  - {posts_expired} posts expired")
        print(f"  - {comments_expired} comments expired")
        
        return True
    except Exception as e:
        print(f"✗ Worker failed: {e}")
        return False


if __name__ == "__main__":
    # Run the worker
    success = run_expiration_worker()
    sys.exit(0 if success else 1)
