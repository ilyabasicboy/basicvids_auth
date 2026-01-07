from fastapi import FastAPI
from basicvids_auth.routers.root import router as root_router
from basicvids_auth.routers.users import router as users_router
from basicvids_auth.routers.auth import router as auth_router

app = FastAPI()


app.include_router(root_router, prefix='/api/v1')
app.include_router(users_router, prefix='/api/v1')
app.include_router(auth_router, prefix='/api/v1')