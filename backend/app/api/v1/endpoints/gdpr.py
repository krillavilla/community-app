from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.services.gdpr_service import GDPRService
from app.models.user import User
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/export")
def export_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export all user data (GDPR Article 20 - Right to Data Portability)
    
    Returns all personal data in machine-readable JSON format
    """
    logger.info(f"GDPR export requested for user {current_user.id}")
    
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
    - Posts and comments are soft-deleted (retained for 30 days for moderation)
    - User profile is anonymized immediately
    - All data permanently deleted after 30 days
    """
    logger.warning(f"GDPR account deletion requested for user {current_user.id}")
    
    success = GDPRService.delete_user_data(str(current_user.id), db)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete account")
    
    return {
        "message": "Account deleted successfully",
        "deleted_at": GDPRService.export_user_data.__module__,
        "note": "Your content will be permanently removed after 30 days"
    }
