"""
Authentication dependencies for protected routes.
Implements get_or_create user pattern from Auth0 JWT.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import jwt_bearer
from app.api.deps.db import get_db
from app.models.user import User, UserRole, TrustLevel


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Creates user on first login (Auth0 pattern).
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
        
    Returns:
        Authenticated User object
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    try:
        # Verify token and extract payload
        payload = await jwt_bearer.verify_token(token)
        auth0_sub = payload.get("sub")
        
        if not auth0_sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing 'sub' claim"
            )
        
        # Get or create user
        user = db.query(User).filter(User.auth0_sub == auth0_sub).first()
        
        if not user:
            # First login - create user
            email = payload.get("email")
            name = payload.get("name", payload.get("email", "User"))
            
            user = User(
                auth0_sub=auth0_sub,
                email=email,
                display_name=name,
                role=UserRole.USER,
                trust_level=TrustLevel.NEW_SPROUT,
                spiritual_opt_in=False  # Default to secular content
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def require_guardian(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require Guardian role for endpoint access.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        User if Guardian
        
    Raises:
        HTTPException: If user is not Guardian
    """
    if current_user.role != UserRole.GUARDIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guardian access required"
        )
    return current_user


async def require_guide(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require verified Guide status for endpoint access.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        User if verified Guide
        
    Raises:
        HTTPException: If user is not verified Guide
    """
    if not current_user.is_verified_guide:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verified Guide status required"
        )
    return current_user


async def require_good_soil(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require Good Soil trust level or higher.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        User if Good Soil or Flourishing
        
    Raises:
        HTTPException: If trust level insufficient
    """
    if current_user.trust_level not in [TrustLevel.GOOD_SOIL, TrustLevel.FLOURISHING]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Good Soil trust level required. Continue contributing to the community to increase your trust level."
        )
    return current_user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Useful for endpoints that work for both authenticated and anonymous users.
    
    Args:
        credentials: HTTP Authorization credentials (optional)
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        # TODO: Make this truly async-safe
        return get_current_user(credentials, db)
    except:
        return None
