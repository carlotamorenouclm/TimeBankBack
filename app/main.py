from fastapi import FastAPI
from app.db.session import create_tables
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.me import router as me_router
from app.api.routes.users import router as users_router
from app.api.routes.token import router as token_router

app = FastAPI(title="TimeBankBack")


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(me_router, prefix="/me", tags=["me"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(token_router, prefix="/auth", tags=["auth"])