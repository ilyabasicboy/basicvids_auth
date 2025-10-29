from fastapi import FastAPI
from basicvids_auth.routers.root import router as root_router

app = FastAPI()

app.include_router(root_router)