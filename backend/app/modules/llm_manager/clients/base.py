from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

class BaseLLMClient(ABC):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')

    def _build_url(self, path: str) -> str:
        """
        Build full URL from base_url and path.
        If base_url does not end with /v1, it is added automatically.
        """
        base = self.base_url
        if not base.endswith('/v1'):
            base += '/v1'
        return base + '/' + path.lstrip('/')

    @abstractmethod
    async def get_move_response(self, board: List[List[Optional[str]]], board_size: int, win_sequence: int, player: str, model: str, difficulty: Optional[str] = None) -> str:
        """
        Send request to LLM and return the raw text response.
        """
        pass
