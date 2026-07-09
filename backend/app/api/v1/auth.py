from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.modules.idm.schemas import (
    UserCreate, AuthEmailRequest, AuthVerifyRequest, 
    AuthVerifyResponse, TokenResponse, UserResponse
)
from app.modules.idm.service import IDMService
from app.dependencies import get_idm_service
from app.core.exceptions import AppException

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(
    request: Request,
    data: UserCreate,
    idm_service: IDMService = Depends(get_idm_service)
):
    """Register new user: send verification code to email."""
    await idm_service.register(
        email=data.email,
        username=data.username,
        ip=request.client.host if request.client else "unknown"
    )
    return {"message": "Код отправлен на email", "email": data.email}


@router.post("/verify-registration", response_model=AuthVerifyResponse)
async def verify_registration(
    request: Request,
    data: AuthVerifyRequest,
    idm_service: IDMService = Depends(get_idm_service)
):
    """Verify email code and complete registration."""
    access_token, refresh_token, user = await idm_service.verify_registration(
        email=data.email,
        code=data.code,
        ip=request.client.host if request.client else "unknown"
    )
    return AuthVerifyResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    data: AuthEmailRequest,
    idm_service: IDMService = Depends(get_idm_service)
):
    """Login: send verification code to email."""
    await idm_service.login(
        email=data.email,
        ip=request.client.host if request.client else "unknown"
    )
    return {"message": "Код отправлен на email", "email": data.email}


@router.post("/verify-login", response_model=AuthVerifyResponse)
async def verify_login(
    request: Request,
    data: AuthVerifyRequest,
    idm_service: IDMService = Depends(get_idm_service)
):
    """Verify email code and get tokens."""
    access_token, refresh_token, user = await idm_service.verify_login(
        email=data.email,
        code=data.code,
        ip=request.client.host if request.client else "unknown"
    )
    return AuthVerifyResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    idm_service: IDMService = Depends(get_idm_service)
):
    """Refresh access token using refresh token."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    refresh_token = auth_header.split(" ")[1]
    new_access = await idm_service.refresh(refresh_token)
    return TokenResponse(access_token=new_access, refresh_token="", token_type="bearer")


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    idm_service: IDMService = Depends(get_idm_service)
):
    """Logout: invalidate access token."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    access_token = auth_header.split(" ")[1]
    await idm_service.logout(access_token)
    return {"message": "Успешный выход"}


@router.post("/resend-code", status_code=status.HTTP_200_OK)
async def resend_code(
    data: AuthEmailRequest,
    idm_service: IDMService = Depends(get_idm_service)
):
    """Resend verification code."""
    await idm_service.resend_code(data.email)
    return {"message": "Код отправлен повторно"}


@router.get("/verify", response_model=UserResponse)
async def verify_token(
    request: Request,
    idm_service: IDMService = Depends(get_idm_service)
):
    """Verify access token and return user info."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    access_token = auth_header.split(" ")[1]
    user = await idm_service.verify_token(access_token)
    return user
