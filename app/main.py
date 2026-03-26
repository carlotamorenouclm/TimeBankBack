from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import create_tables
from app.api.routes.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware

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


app.include_router(users_router, prefix="/users", tags=["users"])