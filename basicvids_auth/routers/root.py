from fastapi import APIRouter

router = APIRouter(tags=["Root"])


@router.get("/health")
def health():
    return {"status": "ok"}