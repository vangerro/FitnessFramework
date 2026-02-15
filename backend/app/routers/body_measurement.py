from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def body_measurement_health():
    return {"body_measurement": "ok"}
