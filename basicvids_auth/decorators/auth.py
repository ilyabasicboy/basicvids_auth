from functools import wraps
from fastapi import Request, HTTPException, status

from basicvids_auth.utils.auth import decode_token
from basicvids_auth.schemas import get_session
from basicvids_auth.schemas.users import User as UserDB


def authenticate(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise ValueError
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is incorrect",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only access tokens are allowed",
        )
    
    session = next(get_session())

    user_id = payload.get("sub")
    user = session.get(UserDB, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exists",
        )
    
    return user


def authenticated(view):
    @wraps(view)
    async def wrapper(*args, **kwargs):
        # find Request
        request: Request | None = kwargs.get("request")
        if not request:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if request is None:
            raise RuntimeError("Request not found")

        user = authenticate(request)

        # save user
        request.state.user = user

        return await view(*args, **kwargs)

    return wrapper


def admin_authenticated(view):

    @wraps(view)
    async def wrapper(*args, **kwargs):
        # find Request
        request: Request | None = kwargs.get("request")
        if not request:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if request is None:
            raise RuntimeError("Request not found")

        user = authenticate(request)

        if not user.is_admin:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have no permissions for this request",
        )

        # save user
        request.state.user = user

        return await view(*args, **kwargs)

    return wrapper