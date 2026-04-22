# Configure SQLAlchemy connection and expose one session per request.
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    # Open a session for the current request and close it afterwards.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    # Import Base and models so metadata gets registered.
    from app.models.users import Base  # noqa
    from app.models.users import User  # noqa
    from app.models.portal import ServiceOffer  # noqa
    from app.models.portal import ServiceRequest  # noqa
    from app.models.portal import UserTransaction  # noqa
    from app.models.portal import UserWallet  # noqa
    from app.models.portal import WalletRecharge  # noqa

    Base.metadata.create_all(bind=engine)
    ensure_portal_schema_updates()


def ensure_portal_schema_updates() -> None:
    # create_all creates new tables, but it does not modify existing ones.
    # This lightweight patch keeps the schema aligned with the current app state.
    inspector = inspect(engine)

    schema_updates = {
        "users": {
            "avatar_key": "ALTER TABLE users ADD COLUMN avatar_key VARCHAR(100) NULL",
        },
        "service_offers": {
            "owner_id": "ALTER TABLE service_offers ADD COLUMN owner_id INTEGER NULL",
            "home_service": "ALTER TABLE service_offers ADD COLUMN home_service BOOLEAN NOT NULL DEFAULT 1",
            "address": "ALTER TABLE service_offers ADD COLUMN address VARCHAR(255) NULL",
        },
        "service_requests": {
            "requester_id": "ALTER TABLE service_requests ADD COLUMN requester_id INTEGER NULL",
            "service_offer_id": "ALTER TABLE service_requests ADD COLUMN service_offer_id INTEGER NULL",
            "buyer_transaction_id": "ALTER TABLE service_requests ADD COLUMN buyer_transaction_id INTEGER NULL",
        },
    }

    with engine.begin() as connection:
        if inspector.has_table("users"):
            user_columns = {column["name"] for column in inspector.get_columns("users")}
            if "time_tokens" in user_columns:
                connection.execute(text("ALTER TABLE users DROP COLUMN time_tokens"))

        for table_name, table_updates in schema_updates.items():
            if not inspector.has_table(table_name):
                continue

            existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, sql in table_updates.items():
                if column_name not in existing_columns:
                    connection.execute(text(sql))
