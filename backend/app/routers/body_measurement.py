from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def measurement_health():
    return {"measurement": "ok"}
