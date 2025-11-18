"""
Auth0 JWT validation with JWKS caching.
Implements Udacity Backend Nanodegree JWT pattern.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import httpx
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from fastapi import HTTPException, status
from app.core.config import settings


class Auth0JWTBearer:
    """
    Auth0 JWT validation with JWKS key caching.
    
    Validates RS256 JWT tokens from Auth0:
    - Fetches JWKS from Auth0
    - Caches keys for 24 hours
    - Verifies signature, issuer, and audience
    - Extracts user claims
    """
    
    def __init__(self):
        self.jwks_uri = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        self.jwks_cache: Optional[Dict] = None
        self.cache_timestamp: Optional[datetime] = None
        self.cache_duration = timedelta(hours=24)
    
    async def get_jwks(self) -> Dict:
        """
        Fetch JWKS from Auth0 with caching.
        
        Returns:
            Dict containing JWKS keys
            
        Raises:
            HTTPException: If JWKS fetch fails
        """
        # Check cache validity
        if (
            self.jwks_cache 
            and self.cache_timestamp 
            and datetime.now() - self.cache_timestamp < self.cache_duration
        ):
            return self.jwks_cache
        
        # Fetch fresh JWKS
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_uri, timeout=10.0)
                response.raise_for_status()
                self.jwks_cache = response.json()
                self.cache_timestamp = datetime.now()
                return self.jwks_cache
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to fetch JWKS: {str(e)}"
            )
    
    def get_signing_key(self, token: str, jwks: Dict) -> str:
        """
        Extract signing key from JWKS based on token's kid.
        
        Args:
            token: JWT token string
            jwks: JWKS dictionary
            
        Returns:
            Signing key for verification
            
        Raises:
            HTTPException: If key not found
        """
        try:
            # Decode header without verification to get kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing 'kid' in header"
                )
            
            # Find matching key in JWKS
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    return key
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key"
            )
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token header: {str(e)}"
            )
    
    async def verify_token(self, token: str) -> Dict:
        """
        Verify JWT token and extract payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Dict containing token payload (sub, email, etc.)
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            # Get JWKS
            jwks = await self.get_jwks()
            
            # Get signing key
            signing_key = self.get_signing_key(token, jwks)
            
            # Verify token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=[settings.AUTH0_ALGORITHMS],
                audience=settings.AUTH0_API_AUDIENCE,
                issuer=settings.AUTH0_ISSUER
            )
            
            return payload
            
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except JWTClaimsError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token claims: {str(e)}"
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )


# Global instance
jwt_bearer = Auth0JWTBearer()
