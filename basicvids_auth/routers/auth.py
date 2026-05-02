from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlmodel import Session

from basicvids_auth.schemas import get_session
from basicvids_auth.schemas.auth import RefreshToken
from basicvids_auth.models.auth import LoginRequest, TokenResponse, RefreshRequest
from basicvids_auth.rate_limit import rate_limit_ip
from basicvids_auth.settings import settings
from basicvids_auth.utils.auth import authenticate, decode_token, issue_token_pair

from datetime import datetime, timezone


# Create a router
router = APIRouter(tags=["Auth"], prefix='/auth')


def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
        samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
        path=settings.REFRESH_TOKEN_COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


def clear_refresh_token_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        path=settings.REFRESH_TOKEN_COOKIE_PATH,
        samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
    )


def resolve_refresh_token(request: Request, data: RefreshRequest | None) -> str:
    if data and data.refresh_token:
        return data.refresh_token

    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
    if refresh_token:
        return refresh_token

    raise HTTPException(status_code=401, detail="Refresh token missing")


@router.post(
    "/login/",
    response_model=TokenResponse,
    status_code=201,
    dependencies=[Depends(rate_limit_ip("login", 5, 60))],
)
async def login(login: LoginRequest, response: Response, session: Session = Depends(get_session)) -> TokenResponse:
    auth_data = authenticate(session, login.identifier, login.password)

    if not auth_data:
        raise HTTPException(status_code=401, detail='User is not authenticated')

    set_refresh_token_cookie(response, auth_data["refresh_token"])
    return {
        "access_token": auth_data["access_token"],
        "refresh_token": None,
        "token_type": "bearer",
    }


@router.post(
    "/refresh/",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit_ip("refresh", 30, 60))],
)
async def refresh(
    request: Request,
    response: Response,
    data: RefreshRequest | None = None,
    session: Session = Depends(get_session),
):
    refresh_token = resolve_refresh_token(request, data)
    payload = decode_token(refresh_token)

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
    set_refresh_token_cookie(response, token_pair["refresh_token"])
    return {
        "access_token": token_pair["access_token"],
        "refresh_token": None,
        "token_type": "bearer",
    }


@router.post("/logout/")
async def logout(
    request: Request,
    response: Response,
    data: RefreshRequest | None = None,
    session: Session = Depends(get_session),
):
    refresh_token = resolve_refresh_token(request, data)
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload:
        token = session.get(RefreshToken, payload["jti"])
        if token and token.revoked_at is None:
            token.revoked_at = datetime.now(timezone.utc)
            session.add(token)
            session.commit()

    clear_refresh_token_cookie(response)
    return {"detail": "Logged out"}
