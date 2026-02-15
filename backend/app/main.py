from fastapi import FastAPI
from app.routers import auth, users, weight, body_measurement, workout

app = FastAPI(title="FitnessFramework API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(weight.router, prefix="/weight", tags=["weight"])
app.include_router(body_measurement.router, prefix="/measurements", tags=["measurements"])
app.include_router(workout.router, prefix="/workouts", tags=["workouts"])

@app.get("/health")
def health():
    return {"status": "ok"}
