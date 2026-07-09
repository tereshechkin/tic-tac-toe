from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.idm.service import IDMService
from app.dependencies import get_idm_service
from app.core.exceptions import AppException
from app.modules.idm.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    idm_service: IDMService = Depends(get_idm_service),
):
    # TODO: Implement getting current user from token
    # For now, just return a stub
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
