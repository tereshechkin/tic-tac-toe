import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from app.core.cache import cache
from app.core.exceptions import (
    ConflictException, UnauthorizedException, ValidationException, 
    NotFoundException, RateLimitException, AppException
)
from app.core.security import (
    create_access_token, create_refresh_token, decode_token,
    add_to_blacklist, is_blacklisted, store_refresh_token,
    get_refresh_token_data, delete_refresh_token, delete_all_user_refresh_tokens
)
from app.modules.idm.repository import IDMRepository
from app.modules.idm.schemas import UserResponse
from app.modules.email_manager.service import EmailService
from app.utils.logger import get_logger

logger = get_logger(__name__)


def normalize_email(email: str) -> str:
    """Remove spaces and lowercase."""
    return email.replace(" ", "").lower()


class IDMService:
    def __init__(self, repository: IDMRepository, email_service: EmailService):
        self.repo = repository
        self.email_service = email_service
        self.code_ttl = 300  # 5 minutes
        self.attempts_ttl = 300  # 5 minutes
        self.block_ttl = 300  # 5 minutes
        self.max_attempts = 10

    def _generate_code(self) -> str:
        return ''.join(random.choices(string.digits, k=6))

    def _get_code_key(self, email: str) -> str:
        return f"verification:code:{email}"

    def _get_attempts_key(self, email: str) -> str:
        return f"verification:attempts:{email}"

    def _get_blocked_key(self, email: str) -> str:
        return f"verification:blocked:{email}"

    async def _store_code(self, email: str, code: str) -> None:
        key = self._get_code_key(email)
        await cache.set(key, code, ttl=self.code_ttl)

    async def _get_code(self, email: str) -> Optional[str]:
        key = self._get_code_key(email)
        return await cache.get(key)

    async def _delete_code(self, email: str) -> None:
        key = self._get_code_key(email)
        await cache.delete(key)

    async def _increment_attempts(self, email: str) -> int:
        key = self._get_attempts_key(email)
        count = await cache.client.incr(key)
        if count == 1:
            await cache.client.expire(key, self.attempts_ttl)
        return count

    async def _reset_attempts(self, email: str) -> None:
        key = self._get_attempts_key(email)
        await cache.delete(key)

    async def _is_blocked(self, email: str) -> bool:
        key = self._get_blocked_key(email)
        return await cache.exists(key) > 0

    async def _block_user(self, email: str) -> None:
        key = self._get_blocked_key(email)
        await cache.set(key, "blocked", ttl=self.block_ttl)

    async def _send_verification_code(self, email: str, code: str) -> None:
        # Send via email service (currently logs)
        await self.email_service.send_verification_code(email, code)

    async def _verify_code(self, email: str, code: str) -> bool:
        stored = await self._get_code(email)
        if not stored:
            return False
        return stored == code

    async def _check_and_increment_attempts(self, email: str) -> None:
        """Check if blocked, increment attempts and block if exceeded."""
        if await self._is_blocked(email):
            raise RateLimitException("Too many failed attempts. Please try again later.")
        attempts = await self._increment_attempts(email)
        if attempts > self.max_attempts:
            await self._block_user(email)
            raise RateLimitException("Too many failed attempts. Please try again later.")

    async def _clear_attempts_and_code(self, email: str) -> None:
        await self._delete_code(email)
        await self._reset_attempts(email)

    async def _create_user_session_and_tokens(self, user, ip: str) -> Tuple[str, str, UserResponse]:
        # Create session
        session = await self.repo.create_session(user_id=user.id, ip_address=ip)
        # Cache session in Redis (optional)
        await self._cache_session(session)
        # Generate tokens
        access_token = create_access_token({"sub": str(user.id), "jti": str(uuid.uuid4())})
        refresh_jti = str(uuid.uuid4())
        refresh_token = create_refresh_token({"sub": str(user.id), "jti": refresh_jti})
        # Store refresh token in Redis
        await store_refresh_token(refresh_jti, str(user.id), str(session.id))
        # Build user response - settings already loaded if we used appropriate method
        user_resp = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at,
            theme_preference=user.settings.theme_preference if user.settings else "dark"
        )
        return access_token, refresh_token, user_resp

    async def _cache_session(self, session) -> None:
        # Cache session with TTL 24 hours
        key = f"session:{session.id}"
        data = {
            "id": str(session.id),
            "user_id": str(session.user_id) if session.user_id else None,
            "guest_name": session.guest_name,
            "created_at": session.created_at.isoformat() if session.created_at else None,
        }
        await cache.set(key, data, ttl=86400)

    async def register(self, email: str, username: str, ip: str) -> None:
        email = normalize_email(email)
        existing = await self.repo.get_user_by_email(email)
        if existing:
            raise ConflictException("Email already registered")
        code = self._generate_code()
        await self._store_code(email, code)
        # Store username temporarily
        username_key = f"verification:username:{email}"
        await cache.set(username_key, username, ttl=self.code_ttl)
        # Send email
        await self._send_verification_code(email, code)
        logger.info("Registration code sent", extra={"email": email})

    async def verify_registration(self, email: str, code: str, ip: str) -> Tuple[str, str, UserResponse]:
        email = normalize_email(email)
        # Check attempts and block
        await self._check_and_increment_attempts(email)
        # Verify code
        if not await self._verify_code(email, code):
            raise ValidationException("Invalid verification code")
        # Retrieve username
        username_key = f"verification:username:{email}"
        username = await cache.get(username_key)
        if not username:
            raise ValidationException("Username not found or expired")
        await cache.delete(username_key)
        # Clear attempts and code
        await self._clear_attempts_and_code(email)
        # Create user
        user = await self.repo.create_user(email, username)
        # Reload user with settings (create_user creates settings but we need to load it)
        user = await self.repo.get_user_with_settings(user.id)
        # Create session and tokens
        access_token, refresh_token, user_resp = await self._create_user_session_and_tokens(user, ip)
        # Log event
        await self.repo.create_event(
            session_id=None, 
            user_id=user.id, 
            event_type="LOGIN",
            details={"action": "register"}
        )
        return access_token, refresh_token, user_resp

    async def login(self, email: str, ip: str) -> None:
        email = normalize_email(email)
        user = await self.repo.get_user_by_email(email)
        if not user:
            raise NotFoundException("User not found")
        # Generate code and store
        code = self._generate_code()
        await self._store_code(email, code)
        # Send email
        await self._send_verification_code(email, code)
        logger.info("Login code sent", extra={"email": email})

    async def verify_login(self, email: str, code: str, ip: str) -> Tuple[str, str, UserResponse]:
        email = normalize_email(email)
        # Check attempts and block
        await self._check_and_increment_attempts(email)
        # Verify code
        if not await self._verify_code(email, code):
            # Log error
            await self.repo.create_event(
                session_id=None,
                user_id=None,
                event_type="LOGIN_ERROR",
                error="Invalid code",
                details={"email": email}
            )
            raise ValidationException("Invalid verification code")
        # Get user with settings
        user = await self.repo.get_user_by_email_with_settings(email)
        if not user:
            raise NotFoundException("User not found")
        # Clear attempts and code
        await self._clear_attempts_and_code(email)
        # Create session and tokens
        access_token, refresh_token, user_resp = await self._create_user_session_and_tokens(user, ip)
        # Log event
        await self.repo.create_event(
            session_id=None,
            user_id=user.id,
            event_type="LOGIN",
            details={"action": "login"}
        )
        return access_token, refresh_token, user_resp

    async def refresh(self, refresh_token: str) -> str:
        payload = decode_token(refresh_token)
        if not payload:
            raise UnauthorizedException("Invalid refresh token")
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")
        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedException("Invalid refresh token")
        # Check if blacklisted
        if await is_blacklisted(jti):
            raise UnauthorizedException("Token revoked")
        # Get refresh token data from Redis
        data = await get_refresh_token_data(jti)
        if not data:
            raise UnauthorizedException("Refresh token not found")
        user_id = data.get("user_id")
        session_id = data.get("session_id")
        # Verify user exists
        user = await self.repo.get_user_by_id(uuid.UUID(user_id))
        if not user:
            raise UnauthorizedException("User not found")
        # Generate new access token
        new_access = create_access_token({"sub": str(user.id), "jti": str(uuid.uuid4())})
        return new_access

    async def logout(self, access_token: str) -> None:
        payload = decode_token(access_token)
        if not payload:
            raise UnauthorizedException("Invalid access token")
        # Blacklist access token
        jti = payload.get("jti")
        if jti:
            ttl = 60 * 60 * 24 * 7  # 7 days
            await add_to_blacklist(jti, ttl)
        # Delete all refresh tokens for this user
        sub = payload.get("sub")
        if sub:
            user_id = sub
            await delete_all_user_refresh_tokens(user_id)
            # Log event
            user = await self.repo.get_user_by_id(uuid.UUID(user_id))
            if user:
                await self.repo.create_event(
                    session_id=None,
                    user_id=user.id,
                    event_type="LOGOUT",
                    details={"action": "logout"}
                )

    async def resend_code(self, email: str) -> None:
        email = normalize_email(email)
        code = await self._get_code(email)
        if not code:
            raise NotFoundException("No active verification code found")
        await self._send_verification_code(email, code)
        logger.info("Verification code resent", extra={"email": email})

    async def verify_token(self, access_token: str) -> UserResponse:
        payload = decode_token(access_token)
        if not payload:
            raise UnauthorizedException("Invalid access token")
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")
        jti = payload.get("jti")
        if jti and await is_blacklisted(jti):
            raise UnauthorizedException("Token revoked")
        sub = payload.get("sub")
        if not sub:
            raise UnauthorizedException("Invalid token")
        user = await self.repo.get_user_with_settings(uuid.UUID(sub))
        if not user:
            raise UnauthorizedException("User not found")
        if not user.is_active:
            raise UnauthorizedException("User is inactive")
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at,
            theme_preference=user.settings.theme_preference if user.settings else "dark"
        )
