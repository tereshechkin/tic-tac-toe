from typing import Dict, List, Set, Optional
from fastapi import WebSocket
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections per game session."""

    def __init__(self):
        # session_id -> list of websockets
        self._connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        """Accept a WebSocket and add to session."""
        await websocket.accept()
        if session_id not in self._connections:
            self._connections[session_id] = []
        self._connections[session_id].append(websocket)
        logger.info(f"WebSocket connected for session {session_id}")

    async def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket from session."""
        if session_id in self._connections:
            try:
                self._connections[session_id].remove(websocket)
            except ValueError:
                pass
            if not self._connections[session_id]:
                del self._connections[session_id]
        logger.info(f"WebSocket disconnected for session {session_id}")

    async def send_to_session(self, session_id: str, event: dict) -> None:
        """Send a JSON event to all WebSockets in the session."""
        if session_id not in self._connections:
            return
        connections = self._connections[session_id][:]
        for ws in connections:
            try:
                await ws.send_json(event)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                # Optionally remove dead connections

    async def broadcast_game_state(self, session_id: str, game_state: dict) -> None:
        """Send game_state event."""
        event = {"type": "game_state", "data": game_state}
        await self.send_to_session(session_id, event)

    async def broadcast_move_made(self, session_id: str, player: str, row: int, col: int) -> None:
        """Send move_made event."""
        event = {"type": "move_made", "data": {"player": player, "row": row, "col": col}}
        await self.send_to_session(session_id, event)

    async def broadcast_game_over(self, session_id: str, winner: Optional[str], winning_cells: Optional[list]) -> None:
        """Send game_over event."""
        event = {
            "type": "game_over",
            "data": {
                "winner": winner,
                "winning_cells": winning_cells,
            },
        }
        await self.send_to_session(session_id, event)

    async def broadcast_computer_thinking(self, session_id: str) -> None:
        """Send computer_thinking event."""
        event = {"type": "computer_thinking", "data": {}}
        await self.send_to_session(session_id, event)
