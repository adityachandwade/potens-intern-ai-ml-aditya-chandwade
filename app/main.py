from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="AEGIS AI Banking Triage Agent",
    version="1.0.0"
)

app.include_router(router)