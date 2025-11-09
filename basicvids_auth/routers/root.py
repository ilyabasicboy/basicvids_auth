from fastapi import FastAPI, APIRouter


# Create a router
router = APIRouter(tags=["Root"], prefix='/root')


@router.get("/")
async def root():
    return {'text': 'Hello world'}