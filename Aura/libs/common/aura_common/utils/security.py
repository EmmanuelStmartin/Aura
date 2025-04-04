"""Security utilities for Aura services."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import jwt, JWTError
from passlib.context import CryptContext

from aura_common.config import Settings, get_settings
from aura_common.models.user import TokenData, UserRole


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        Whether the password matches the hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    settings: Optional[Settings] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token.
    
    Args:
        data: Token data
        settings: Settings instance
        expires_delta: Token expiration delta
        
    Returns:
        JWT access token
    """
    if settings is None:
        settings = get_settings()
        
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(
    token: str,
    settings: Optional[Settings] = None
) -> Optional[TokenData]:
    """Decode a JWT access token.
    
    Args:
        token: JWT access token
        settings: Settings instance
        
    Returns:
        Token data if valid, None otherwise
    """
    if settings is None:
        settings = get_settings()
        
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role", UserRole.FREE.value)
        exp: int = payload.get("exp")
        
        if email is None:
            return None
            
        return TokenData(email=email, role=role, exp=exp)
    except JWTError:
        return None 