import json
import httpx
from typing import List, Optional, Tuple
from .base import BaseLLMClient
from ..prompts import build_prompt

class AnthropicClient(BaseLLMClient):
    async def get_move_response(self, board, board_size, win_sequence, player, model, difficulty=None):
        prompt = build_prompt(board, board_size, win_sequence, player, difficulty)
        url = self._build_url("messages")
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 50,
            "temperature": 0.3
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            content = data["content"][0]["text"].strip()
            return content
