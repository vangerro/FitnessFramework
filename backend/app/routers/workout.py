from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def workout_health():
    return {"workout": "ok"}
