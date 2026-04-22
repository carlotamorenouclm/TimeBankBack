# Helper script to create or drop tables manually outside normal startup.
from app.db.session import engine
from app.models.users import Base  # noqa: F401
from app.models.users import User  # noqa: F401
from app.models.portal import ServiceOffer  # noqa: F401
from app.models.portal import ServiceRequest  # noqa: F401
from app.models.portal import UserTransaction  # noqa: F401
from app.models.portal import UserWallet  # noqa: F401
from app.models.portal import WalletRecharge  # noqa: F401


def create_all_tables():
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    create_all_tables()
    print(" Tablas creadas.")
