from fastapi import FastAPI, APIRouter
from models import User

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
async def users() -> list[User]:
    return user_list