# Punto de entrada de FastAPI: crea app, middlewares, startup y registro de rutas.
from fastapi import FastAPI
from app.db.session import create_tables
from app.db.queries_portal import cleanup_seeded_portal_data
from app.db.session import SessionLocal
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.me import router as me_router
from app.api.routes.portal import router as portal_router
from app.api.routes.users import router as users_router
from app.api.routes.admins import router as admins_router
from app.api.routes.token import router as token_router

app = FastAPI(title="TimeBankBack")


@app.on_event("startup")
def on_startup() -> None:
    # Start with the schema ready and remove old demo data automatically.
    create_tables()
    db = SessionLocal()
    try:
        cleanup_seeded_portal_data(db)
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(me_router, prefix="/me", tags=["me"])
app.include_router(portal_router, prefix="/portal", tags=["portal"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(admins_router, prefix="/admins", tags=["admins"])
app.include_router(token_router, prefix="/auth", tags=["auth"])
