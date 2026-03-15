from fastapi import FastAPI
from contextlib import asynccontextmanager

from basicvids_auth.schemas import create_db_and_tables
from basicvids_auth.routers.users import router as users_router
from basicvids_auth.routers.auth import router as auth_router
from basicvids_auth.routers.root import router as root_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI()


app.include_router(users_router, prefix='/api/v1')
app.include_router(auth_router, prefix='/api/v1')
app.include_router(root_router)