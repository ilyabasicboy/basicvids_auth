from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from sqlmodel import Session, select

from basicvids_auth.utils.other import is_email
from basicvids_auth.utils.password import verify_password
from basicvids_auth.schemas.users import User as UserDB
from basicvids_auth.schemas.auth import RefreshToken
from basicvids_auth.settings import settings


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    to_encode.update(
        {
            "exp": expire,
            "iat": now
        }
    )
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: str):
    return create_token(
        {"sub": str(user_id), "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str, token_id: str):
    return create_token(
        {"sub": str(user_id), "jti": str(token_id), "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as e:
        print(e)
        return None
    

def authenticate(session: Session, identifier: str, password: str):
    
    query = select(UserDB)

    if is_email(identifier):
        query = query.where(UserDB.email == identifier)
    else:
        query = query.where(UserDB.username == identifier)

    user = session.exec(query).first()

    if not user or not verify_password(password, user.password):
        return
    
    iat = datetime.now(timezone.utc)
    exp = iat + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token = RefreshToken(
        user_id=user.id,
        expires_at=exp,
        created_at=iat
    )
    
    session.add(refresh_token)
    session.commit()
    session.refresh(refresh_token)

    return {
        'access_token': create_access_token(user_id=user.id),
        'refresh_token': create_refresh_token(user_id=user.id, token_id=refresh_token.id)
    }