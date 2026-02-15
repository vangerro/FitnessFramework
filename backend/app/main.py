from fastapi import FastAPI

app = FastAPI(title="FitnessFramework API")

@app.get("/health")
def health():
    return {"status": "ok"}
