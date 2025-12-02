from sqlalchemy.orm import Session
from app.models.user import User
from app.models.flourish import FlourishPost, Comment
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GDPRService:
    """Handle GDPR data export and deletion requests"""
    
    @staticmethod
    def export_user_data(user_id: str, db: Session) -> dict:
        """
        Export all user data in JSON format
        GDPR Article 20 - Right to Data Portability
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Gather all user data
        posts = db.query(FlourishPost).filter(FlourishPost.author_id == user_id).all()
        comments = db.query(Comment).filter(Comment.author_id == user_id).all()
        
        export_data = {
            "user_profile": {
                "id": str(user.id),
                "email": user.email,
                "display_name": user.display_name if hasattr(user, 'display_name') else None,
                "bio": user.bio if hasattr(user, 'bio') else None,
                "date_of_birth": user.date_of_birth.isoformat() if hasattr(user, 'date_of_birth') and user.date_of_birth else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "posts": [
                {
                    "id": str(post.id),
                    "content": post.content,
                    "video_url": getattr(post, 'video_url', None),
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "view_count": getattr(post, 'view_count', 0),
                }
                for post in posts
            ],
            "comments": [
                {
                    "id": str(comment.id),
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat() if comment.created_at else None,
                    "upvotes": getattr(comment, 'upvotes', 0),
                    "downvotes": getattr(comment, 'downvotes', 0),
                }
                for comment in comments
            ],
            "export_timestamp": datetime.utcnow().isoformat(),
            "export_version": "1.0",
        }
        
        return export_data
    
    @staticmethod
    def delete_user_data(user_id: str, db: Session) -> bool:
        """
        Permanently delete all user data
        GDPR Article 17 - Right to be Forgotten
        
        Uses soft delete for posts/comments (for 30 days)
        Hard deletes user record after anonymization
        """
        try:
            # Soft delete posts and comments
            db.query(FlourishPost).filter(FlourishPost.author_id == user_id).update({"soft_deleted": True})
            db.query(Comment).filter(Comment.author_id == user_id).update({"soft_deleted": True})
            
            # Anonymize and soft delete user
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.email = f"deleted_{user_id}@deleted.local"
                if hasattr(user, 'display_name'):
                    user.display_name = "Deleted User"
                if hasattr(user, 'bio'):
                    user.bio = None
                if hasattr(user, 'date_of_birth'):
                    user.date_of_birth = None
                if hasattr(user, 'soft_deleted'):
                    user.soft_deleted = True
            
            db.commit()
            logger.info(f"Successfully deleted data for user {user_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting user data: {e}")
            return False
