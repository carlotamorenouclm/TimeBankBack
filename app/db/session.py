from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    # Importa Base y modelos para registrar metadata
    from app.models.users import Base  # noqa
    from app.models.users import User  # noqa
    from app.models.portal import ServiceOffer  # noqa
    from app.models.portal import ServiceRequest  # noqa
    from app.models.portal import UserTransaction  # noqa
    from app.models.portal import UserWallet  # noqa
    from app.models.portal import WalletRecharge  # noqa

    Base.metadata.create_all(bind=engine)
