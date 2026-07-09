from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from app.modules.idm.models import User, UserSettings, Session, Event
from app.core.exceptions import ConflictException, DatabaseException, NotFoundException


class IDMRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email_with_settings(self, email: str) -> User | None:
        """Get user with settings preloaded."""
        stmt = select(User).where(User.email == email).options(selectinload(User.settings))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, email: str, username: str) -> User:
        user = User(email=email, username=username)
        self.db.add(user)
        try:
            await self.db.flush()  # get id
            # Create default settings
            settings = UserSettings(user_id=user.id, theme_preference="dark")
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError as e:
            await self.db.rollback()
            if "email" in str(e).lower():
                raise ConflictException("Email already registered")
            raise DatabaseException("Failed to create user")

    async def create_session(self, user_id: UUID | None, ip_address: str | None, guest_name: str | None = None) -> Session:
        session = Session(user_id=user_id, ip_address=ip_address, guest_name=guest_name)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: UUID) -> Session | None:
        stmt = select(Session).where(Session.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_event(self, session_id: UUID | None, user_id: UUID | None, event_type: str, error: str | None = None, details: dict | None = None) -> Event:
        event = Event(session_id=session_id, user_id=user_id, event_type=event_type, error=error, details_json=details)
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def update_user_settings(self, user_id: UUID, theme_preference: str) -> None:
        stmt = update(UserSettings).where(UserSettings.user_id == user_id).values(theme_preference=theme_preference)
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_user_with_settings(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id).options(selectinload(User.settings))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
