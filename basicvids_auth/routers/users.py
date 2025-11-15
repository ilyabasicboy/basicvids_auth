from fastapi import FastAPI, APIRouter
from fastapi import Depends

from sqlmodel import Session

from utils.password import hash_password
from schemas import get_session, User as UserDB
from models import User, PublicUser, UserCreate

# Create a router for users
router = APIRouter(tags=["Users"], prefix='/users')


user_list = [
    User(
        username='test',
        email='test@test.ru',
        password='test'
    )
]


@router.get("/")
async def users() -> list[PublicUser]:
    return user_list


@router.post("/create/", response_model=PublicUser)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    # hash the password
    user_data = user.model_dump()
    user_data["password"] = hash_password(user.password)

    db_user = UserDB(**user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user