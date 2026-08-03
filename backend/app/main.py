from fastapi import FastAPI

app = FastAPI(
    title="Tasks API",
    description="API for managing tasks",
    version="1.0.0"
)

@app.get("/")
def root():
    return{
        "name": "Tasks API",
        "version": "1.0.0",
        "status":"running",
    }


@app.get("/health")
def health():
    return {"status":"ok"}