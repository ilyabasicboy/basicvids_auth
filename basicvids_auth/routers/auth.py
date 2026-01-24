from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from basicvids_auth.schemas import get_session
from basicvids_auth.schemas.auth import RefreshToken
from basicvids_auth.models.auth import LoginRequest, TokenResponse, RefreshRequest
from basicvids_auth.utils.auth import authenticate, decode_token, create_access_token

from datetime import datetime, timezone


# Create a router
router = APIRouter(tags=["Auth"], prefix='/auth')


@router.post("/login/", response_model=TokenResponse, status_code=201)
async def login(login: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    auth_data = authenticate(session, login.identifier, login.password)

    if not auth_data:
        raise HTTPException(status_code=401, detail='User is not authenticated')

    return auth_data


@router.post("/refresh/", response_model=TokenResponse)
def refresh(data: RefreshRequest, session: Session = Depends(get_session)):
    payload = decode_token(data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token = session.get(RefreshToken, payload["jti"])

    if not token or token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    access_token = create_access_token(token.user_id)

    return {
        "access_token": access_token,
        "refresh_token": data.refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout/")
def logout(data: RefreshRequest, session: Session = Depends(get_session)):
    payload = decode_token(data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload:
        token = session.get(RefreshToken, payload["jti"])
        session.delete(token)
        session.commit()

    return {"detail": "Logged out"}