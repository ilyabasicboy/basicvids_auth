from fastapi import FastAPI, APIRouter
from models import User, PublicUser

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