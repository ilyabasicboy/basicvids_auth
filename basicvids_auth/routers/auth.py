from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from basicvids_auth.schemas import get_session
from basicvids_auth.schemas.auth import RefreshToken
from basicvids_auth.models.auth import LoginRequest, TokenResponse, RefreshRequest
from basicvids_auth.rate_limit import rate_limit_ip
from basicvids_auth.utils.auth import authenticate, decode_token, issue_token_pair

from datetime import datetime, timezone


# Create a router
router = APIRouter(tags=["Auth"], prefix='/auth')


@router.post(
    "/login/",
    response_model=TokenResponse,
    status_code=201,
    dependencies=[Depends(rate_limit_ip("login", 5, 60))],
)
async def login(login: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    auth_data = authenticate(session, login.identifier, login.password)

    if not auth_data:
        raise HTTPException(status_code=401, detail='User is not authenticated')

    return auth_data


@router.post(
    "/refresh/",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit_ip("refresh", 30, 60))],
)
async def refresh(data: RefreshRequest, session: Session = Depends(get_session)):
    payload = decode_token(data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token = session.get(RefreshToken, payload["jti"])

    if (
        not token
        or token.revoked_at is not None
        or token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    token.revoked_at = datetime.now(timezone.utc)
    session.add(token)
    session.commit()

    token_pair = issue_token_pair(session, token.user_id)
    return {
        **token_pair,
        "token_type": "bearer",
    }


@router.post("/logout/")
async def logout(data: RefreshRequest, session: Session = Depends(get_session)):
    payload = decode_token(data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload:
        token = session.get(RefreshToken, payload["jti"])
        if token and token.revoked_at is None:
            token.revoked_at = datetime.now(timezone.utc)
            session.add(token)
            session.commit()

    return {"detail": "Logged out"}
