from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def auth_health():
    return {"auth": "ok"}
