from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.db.connection import AsyncSessionLocal
from app.core.cache import cache
from app.modules.idm.repository import IDMRepository
from app.modules.idm.service import IDMService
from app.modules.idm.schemas import UserResponse
from app.modules.email_manager.sender import EmailSender
from app.modules.email_manager.service import EmailService
from app.modules.game_engine import GameEngineService, WebSocketManager
from app.modules.game_engine.repository import GameRepository
from app.modules.llm_manager import LLMManagerService
from app.modules.llm_manager.repository import LLMRepository
from app.modules.game_repository.service import GameListService

# Global WebSocket manager instance
_websocket_manager = WebSocketManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis() -> Redis:
    return cache.client


async def get_email_sender() -> EmailSender:
    return EmailSender()


async def get_email_service(
    sender: EmailSender = Depends(get_email_sender)
) -> EmailService:
    return EmailService(sender)


async def get_idm_service(
    db: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service)
) -> IDMService:
    repo = IDMRepository(db)
    return IDMService(repo, email_service)


async def get_websocket_manager() -> WebSocketManager:
    return _websocket_manager


async def get_llm_manager_service(
    db: AsyncSession = Depends(get_db)
) -> LLMManagerService:
    repo = LLMRepository(db)
    return LLMManagerService(repo)


async def get_game_repository(
    db: AsyncSession = Depends(get_db)
) -> GameRepository:
    return GameRepository(db)


async def get_game_engine_service(
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
    llm_manager: LLMManagerService = Depends(get_llm_manager_service),
    game_repo: GameRepository = Depends(get_game_repository),
) -> GameEngineService:
    return GameEngineService(ws_manager, llm_manager, game_repo)


async def get_game_list_service(
    db: AsyncSession = Depends(get_db)
) -> GameListService:
    return GameListService(db)


async def get_current_user(
    request: Request,
    idm_service: IDMService = Depends(get_idm_service)
) -> UserResponse:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )
    token = auth_header.split(" ")[1]
    user = await idm_service.verify_token(token)
    return user
