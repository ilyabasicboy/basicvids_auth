from fastapi import FastAPI, APIRouter, Depends, Query, HTTPException, Path, Request

from sqlmodel import Session, select

from typing import Annotated

from basicvids_auth.utils.password import hash_password
from basicvids_auth.schemas import get_session
from basicvids_auth.schemas.users import User as UserDB
from basicvids_auth.models.users import User, PublicUser, UserCreate, FilterUser
from basicvids_auth.decorators.auth import authenticated, admin_authenticated

# Create a router for users
router = APIRouter(tags=["Users"], prefix='/users')


@router.get("/")
@admin_authenticated
async def users(
    request: Request,
    filter: Annotated[FilterUser, Depends(FilterUser)],
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


@router.get("/detail/")
@authenticated
async def users_detail(
    request: Request,
) -> PublicUser:
    user = request.state.user

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.get("/detail/{user_id}")
@admin_authenticated
async def users_detail_by_id(
    request: Request,
    user_id: Annotated[int, Path(title="The ID of the user to get")],
    session: Session = Depends(get_session),
) -> PublicUser:
    user = session.get(UserDB, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/create/", response_model=PublicUser, status_code=201)
async def create_user(user: UserCreate, session: Session = Depends(get_session)) -> PublicUser:

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


@router.delete('/delete/', status_code=200)
@authenticated
async def delete_user(
    request: Request,
    session: Session = Depends(get_session)
):
    authenticated_user = request.state.user
    user = session.get(UserDB, authenticated_user.id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()

    return {"message": "User deleted successfully"}


@router.delete('/delete/{user_id}', status_code=200)
@admin_authenticated
async def delete_user_by_id(
    request: Request,
    user_id: Annotated[int, Path(title="The ID of the user to delete")],
    session: Session = Depends(get_session)
):
    user = session.get(UserDB, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()

    return {"message": "User deleted successfully"}