from fastapi import FastAPI, APIRouter, Depends, Query, HTTPException

from sqlmodel import Session, select

from typing import Annotated

from basicvids_auth.utils.password import hash_password
from basicvids_auth.schemas import get_session, User as UserDB
from basicvids_auth.models import User, PublicUser, UserCreate

# Create a router for users
router = APIRouter(tags=["Users"], prefix='/users')


@router.get("/")
async def users(
    filter: Annotated[PublicUser, Depends(PublicUser)],
    offset:int = 0,
    limit: int = Query(default=10, le=100),
    session: Session = Depends(get_session),
) -> list[PublicUser]:
    
    query = select(UserDB)

    # Dynamically apply filters for non-None values
    filter_dict = filter.model_dump(exclude_none=True)
    for field, value in filter_dict.items():
        if hasattr(UserDB, field):
            query = query.where(getattr(UserDB, field) == value)

    users = session.exec(query.offset(offset).limit(limit)).all()
    return users


@router.post("/create/", response_model=PublicUser, status_code=201)
def create_user(user: UserCreate, session: Session = Depends(get_session)) -> PublicUser:

    # Check duplicates
    query = select(UserDB)
    for field, value in user.model_dump(exclude={'password'}).items():
        if hasattr(UserDB, field):
            query = query.where(getattr(UserDB, field) == value)

    existing_user = session.exec(query).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='User already exists')

    user_data = user.model_dump()

    # hash the password
    user_data["password"] = hash_password(user.password)

    db_user = UserDB(**user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user