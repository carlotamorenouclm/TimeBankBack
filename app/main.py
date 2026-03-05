from fastapi import FastAPI
from app.db.session import create_tables
from app.api.routes.users import router as users_router

app = FastAPI(title="TimeBankBack")


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(users_router, prefix="/users", tags=["users"])