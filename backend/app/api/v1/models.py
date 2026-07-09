from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.modules.llm_manager.service import LLMManagerService
from app.modules.llm_manager.schemas import ModelResponse, ModelListResponse
from app.dependencies import get_llm_manager_service
from app.core.exceptions import AppException

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=ModelListResponse)
async def list_models(
    llm_manager: LLMManagerService = Depends(get_llm_manager_service),
):
    """
    Get list of available LLM models.
    
    Returns all models from the database with their status.
    """
    try:
        models = await llm_manager.list_models()
        return ModelListResponse(models=models)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
