from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()

# CryptContext handles bcrypt hashing
# 'deprecated=auto' means old hash schemes are auto-upgraded on verify
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    print(f"[HASH] Original password length (chars): {len(password)}")
    password_bytes = password.encode("utf-8")
    print(f"[HASH] Bytes length: {len(password_bytes)}")
    
    if len(password_bytes) > 72:
        print("[HASH] Truncating password to 72 bytes")
        password_bytes = password_bytes[:72]
    
    try:
        password_truncated = password_bytes.decode("utf-8", errors="ignore")
        print(f"[HASH] Truncated string length: {len(password_truncated)}")
        hashed = pwd_context.hash(password_truncated)
        print("[HASH] Hashing succeeded")
        return hashed
    except Exception as e:
        print(f"[HASH] Hashing FAILED: {str(e)}")
        raise


def verify_password(plain: str, hashed: str) -> bool:
    """bcrypt.verify handles the salt extraction automatically."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()

    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload["exp"] = expire

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Raises jose.JWTError if token is invalid or expired."""
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )