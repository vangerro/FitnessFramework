from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def weight_health():
    return {"weight": "ok"}
