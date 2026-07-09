import json
import httpx
from typing import List, Optional, Tuple
from .base import BaseLLMClient
from ..prompts import build_prompt

class GoogleClient(BaseLLMClient):
    async def get_move_response(self, board, board_size, win_sequence, player, model, difficulty=None):
        prompt = build_prompt(board, board_size, win_sequence, player, difficulty)
        # Google API uses a different path pattern: /v1/models/{model}:generateContent
        path = f"models/{model}:generateContent"
        url = self._build_url(path)  # base will add /v1 automatically, so final is /v1/models/{model}:generateContent
        headers = {
            "Content-Type": "application/json"
        }
        params = {"key": self.api_key}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 50
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, params=params, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return content
