from fastapi import FastAPI, APIRouter


# Create a router
router = APIRouter(tags=["Auth"], prefix='/auth')


@router.get("/")
async def root():
    return {'text': 'Hello world'}