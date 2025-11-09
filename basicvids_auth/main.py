from fastapi import FastAPI
from routers.root import router as root_router
from routers.users import router as users_router

app = FastAPI()

app.include_router(root_router, prefix='/api/v1')
app.include_router(users_router, prefix='/api/v1')