from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import create_tables
from app.api.routes.users import router as users_router
from app.api.routes.auth import router as auth_router
from app.api.routes.profile import router as profile_router

app = FastAPI(title="TimeBankBack")


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(profile_router, prefix="/profile", tags=["profile"])