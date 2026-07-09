import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

from jose import JWTError, jwt
from app.config import settings
from app.core.cache import cache

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    if "jti" not in to_encode:
        to_encode["jti"] = str(uuid.uuid4())
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    if "jti" not in to_encode:
        to_encode["jti"] = str(uuid.uuid4())
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return {}


async def add_to_blacklist(jti: str, ttl_seconds: int) -> None:
    """Add token jti to blacklist with TTL."""
    key = f"blacklist:{jti}"
    await cache.set(key, "revoked", ttl=ttl_seconds, serialize=False)


async def is_blacklisted(jti: str) -> bool:
    return await cache.exists(f"blacklist:{jti}")


async def store_refresh_token(jti: str, user_id: str, session_id: str) -> None:
    key = f"refresh_token:{jti}"
    value = {"user_id": user_id, "session_id": session_id}
    ttl = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # seconds
    await cache.set(key, value, ttl=ttl)
    # Add to user's refresh token set
    await add_user_refresh_token(user_id, jti)


async def get_refresh_token_data(jti: str) -> Optional[Dict[str, Any]]:
    key = f"refresh_token:{jti}"
    data = await cache.get(key)
    if data:
        return data
    return None


async def delete_refresh_token(jti: str) -> None:
    key = f"refresh_token:{jti}"
    await cache.delete(key)


async def add_user_refresh_token(user_id: str, jti: str) -> None:
    key = f"user_refresh_tokens:{user_id}"
    await cache.client.sadd(key, jti)
    await cache.client.expire(key, REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)


async def remove_user_refresh_token(user_id: str, jti: str) -> None:
    key = f"user_refresh_tokens:{user_id}"
    await cache.client.srem(key, jti)


async def get_user_refresh_tokens(user_id: str) -> set:
    key = f"user_refresh_tokens:{user_id}"
    return await cache.client.smembers(key)


async def delete_all_user_refresh_tokens(user_id: str) -> None:
    key = f"user_refresh_tokens:{user_id}"
    jtis = await cache.client.smembers(key)
    for jti in jtis:
        await delete_refresh_token(jti)
    await cache.delete(key)
