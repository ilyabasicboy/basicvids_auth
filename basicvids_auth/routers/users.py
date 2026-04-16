from fastapi import FastAPI, APIRouter, Depends, Query, HTTPException, Path, Request

from sqlmodel import Session, select
from sqlalchemy import or_

from typing import Annotated

from basicvids_auth.utils.password import hash_password, verify_password
from basicvids_auth.schemas import get_session
from basicvids_auth.schemas.users import User as UserDB
from basicvids_auth.models.users import User, PublicUser, UserChange, UserCreate, UserPasswordChange, UserPasswordChangeResponse, FilterUser, AdminCreate
from basicvids_auth.decorators.auth import authenticated, admin_authenticated

# Create a router for users
router = APIRouter(tags=["Users"], prefix='/users')


def get_existing_user(session: Session, username: str, email: str) -> UserDB | None:
    statement = select(UserDB).where(
        or_(UserDB.username == username, UserDB.email == email)
    )
    return session.exec(statement).first()


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
    session: Session = Depends(get_session),
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
    existing_user = get_existing_user(session, user.username, user.email)
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


@router.post("/create/admin/", response_model=PublicUser, status_code=201)
@admin_authenticated
async def create_admin(
    request: Request,
    user: AdminCreate,
    session: Session = Depends(get_session)
) -> PublicUser:
    existing_user = get_existing_user(session, user.username, user.email)
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


@router.patch("/change/", response_model=PublicUser, status_code=200)
@authenticated
async def change_user(
    request: Request,
    user: UserChange,
    session: Session = Depends(get_session),
) -> PublicUser:
    authenticated_user = request.state.user
    db_user = session.get(UserDB, authenticated_user.id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.model_dump()
    for field, value in user_data.items():
        setattr(db_user, field, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.patch("/change/password/", response_model=UserPasswordChangeResponse, status_code=200)
@authenticated
async def change_user_password(
    request: Request,
    data: UserPasswordChange,
    session: Session = Depends(get_session),
) -> UserPasswordChangeResponse:
    authenticated_user = request.state.user
    db_user = session.get(UserDB, authenticated_user.id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.old_password, db_user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    db_user.password = hash_password(data.new_password)
    session.add(db_user)
    session.commit()
    return UserPasswordChangeResponse(message="Password changed successfully")


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
