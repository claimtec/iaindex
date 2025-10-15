"""
Authentication middleware and utilities
"""
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from ..config import settings

logger = logging.getLogger(__name__)

# Security schemes
bearer_scheme = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class AuthService:
    """Authentication service"""

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token

        Args:
            data: Data to encode in token
            expires_delta: Optional expiry duration

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token to verify

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def verify_api_key(api_key: str) -> bool:
        """
        Verify API key (placeholder - implement with database lookup)

        Args:
            api_key: API key to verify

        Returns:
            True if valid
        """
        # TODO: Implement database lookup for API keys
        # For now, this is a placeholder
        return len(api_key) >= 32


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT

    Args:
        credentials: Bearer token credentials

    Returns:
        User information from token

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = AuthService.verify_token(token)

    if not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    return payload


async def get_api_key(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> str:
    """
    Dependency to verify API key or JWT token

    Args:
        api_key: API key from header
        credentials: Bearer token credentials

    Returns:
        Verified API key or user identifier

    Raises:
        HTTPException: If authentication fails
    """
    # Try JWT first
    if credentials:
        try:
            payload = AuthService.verify_token(credentials.credentials)
            return payload.get("sub", "unknown")
        except HTTPException:
            pass

    # Try API key
    if api_key:
        if AuthService.verify_api_key(api_key):
            return api_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def optional_auth(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> Optional[str]:
    """
    Optional authentication dependency

    Returns:
        User identifier if authenticated, None otherwise
    """
    try:
        return await get_api_key(api_key, credentials)
    except HTTPException:
        return None
