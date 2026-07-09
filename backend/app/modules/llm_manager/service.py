import random
import asyncio
from typing import List, Optional, Tuple
from uuid import UUID

from app.config import settings
from app.core.exceptions import LLMServiceException, NotFoundException, ValidationException
from app.modules.llm_manager.repository import LLMRepository
from app.modules.llm_manager.verifier import parse_move_response
from app.modules.llm_manager.clients.openai import OpenAIClient
from app.modules.llm_manager.clients.anthropic import AnthropicClient
from app.modules.llm_manager.clients.google import GoogleClient
from app.modules.game_engine.logic import get_available_moves
from app.modules.llm_manager.schemas import ModelResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

class LLMManagerService:
    def __init__(self, repository: LLMRepository):
        self.repo = repository
        # Map manufacturer to client class and settings
        self.provider_map = {
            "OpenAI": (OpenAIClient, settings.OPENAI_API_KEY, settings.OPENAI_BASE_URL),
            "Anthropic": (AnthropicClient, settings.ANTHROPIC_API_KEY, settings.ANTHROPIC_BASE_URL),
            "Google": (GoogleClient, settings.GOOGLE_API_KEY, settings.GOOGLE_BASE_URL),
        }
        self.max_retries = 3
        self.retry_delays = [1, 2, 4]  # seconds

    async def get_move(
        self,
        board: List[List[Optional[str]]],
        board_size: int,
        win_sequence: int,
        player: str,
        model_id: Optional[UUID] = None,
        difficulty: Optional[str] = None,
    ) -> Tuple[int, int]:
        """
        Get a move from the LLM.
        """
        # If model_id not provided, pick first enabled model
        if model_id is None:
            models = await self.repo.list_models(enabled_only=True)
            if not models:
                raise LLMServiceException("No enabled LLM models available")
            model = models[0]
        else:
            model = await self.repo.get_model_by_id(model_id)
            if not model.enabled:
                raise LLMServiceException("Model is disabled")

        # Determine client based on manufacturer
        manufacturer = model.manufacturer
        if manufacturer not in self.provider_map:
            raise LLMServiceException(f"Unsupported manufacturer: {manufacturer}")

        client_class, api_key, base_url = self.provider_map[manufacturer]
        if not api_key or not base_url:
            raise LLMServiceException(f"API credentials missing for {manufacturer}")

        client = client_class(api_key, base_url)

        # Try up to max_retries times with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response_text = await client.get_move_response(
                    board=board,
                    board_size=board_size,
                    win_sequence=win_sequence,
                    player=player,
                    model=model.model_key,
                    difficulty=difficulty,
                )
                logger.info(f"LLM response: {response_text}")
                move = parse_move_response(response_text, board)
                if move is not None:
                    row, col = move
                    if board[row][col] is None:
                        return row, col
                    else:
                        logger.warning(f"LLM returned occupied cell ({row},{col}), retrying")
                else:
                    logger.warning(f"LLM response invalid format, retrying")
                # If we reach here, move was invalid, so we continue to retry
            except Exception as e:
                logger.error(f"LLM request failed (attempt {attempt+1}/{self.max_retries}): {e}")
                last_exception = e
                # Check if it's a rate limit (429) - we should wait longer
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                    # Wait 5 seconds for rate limit, then retry
                    wait_time = 5 + attempt * 5  # 5, 10, 15 seconds
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                    continue

            # Wait before next attempt (unless it's the last attempt)
            if attempt < self.max_retries - 1:
                delay = self.retry_delays[attempt]
                logger.info(f"Waiting {delay}s before retry")
                await asyncio.sleep(delay)

        # All retries exhausted
        if last_exception:
            logger.error(f"All LLM attempts failed, falling back to random move")

        # Fallback to random valid move
        available = get_available_moves(board)
        if not available:
            raise ValidationException("No available moves")
        row, col = random.choice(available)
        logger.warning(f"Falling back to random move ({row},{col})")
        return row, col

    async def list_models(self) -> List[ModelResponse]:
        """
        Get list of all LLM models from database.
        """
        models = await self.repo.list_models(enabled_only=False)
        return [
            ModelResponse(
                id=model.id,
                name=model.name,
                description=model.description,
                type=model.model_type,  # type: ignore
                enabled=model.enabled,
                manufacturer=model.manufacturer,
                release_date=model.release_date,
            )
            for model in models
        ]
