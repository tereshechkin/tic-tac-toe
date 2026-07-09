from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from uuid import UUID

from app.dependencies import get_game_engine_service, get_websocket_manager
from app.modules.game_engine import GameEngineService, WebSocketManager
from app.core.exceptions import NotFoundException
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.websocket("/ws/games/{session_id}")
async def websocket_game(
    websocket: WebSocket,
    session_id: UUID,
    game_engine: GameEngineService = Depends(get_game_engine_service),
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
):
    """WebSocket endpoint for game session."""
    # Verify game exists
    try:
        await game_engine.get_game_state(session_id)
    except NotFoundException:
        await websocket.close(code=1008, reason="Game not found")
        return

    # Accept connection
    await ws_manager.connect(str(session_id), websocket)

    try:
        # Send initial state
        state = await game_engine.get_game_state(session_id)
        await websocket.send_json({"type": "game_state", "data": state.to_redis_dict()})

        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "make_move":
                # Client makes a move
                player = data.get("player")
                row = data.get("row")
                col = data.get("col")
                if player not in ("X", "O") or row is None or col is None:
                    await websocket.send_json({"type": "error", "data": {"message": "Invalid move data"}})
                    continue
                try:
                    # Validate turn: we should check if it's this player's turn
                    # For simplicity, the client sends the player; we'll trust but engine will validate
                    await game_engine.make_move(session_id, player, row, col)
                except Exception as e:
                    await websocket.send_json({"type": "error", "data": {"message": str(e)}})

            elif msg_type == "request_computer_move":
                # Client requests computer move
                try:
                    await game_engine.request_computer_move(session_id)
                except Exception as e:
                    await websocket.send_json({"type": "error", "data": {"message": str(e)}})

            elif msg_type == "restart":
                try:
                    await game_engine.restart_game(session_id)
                except Exception as e:
                    await websocket.send_json({"type": "error", "data": {"message": str(e)}})

            elif msg_type == "exit":
                await game_engine.exit_game(session_id)
                await websocket.send_json({"type": "exit", "data": {"message": "Game exited"}})
                # Close connection
                await websocket.close()
                break

            else:
                await websocket.send_json({"type": "error", "data": {"message": f"Unknown message type: {msg_type}"}})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    finally:
        await ws_manager.disconnect(str(session_id), websocket)
