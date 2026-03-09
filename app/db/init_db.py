from app.db.session import engine
from app.models.users import Base  # noqa: F401
from app.models.users import User  # noqa: F401


def create_all_tables():
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    create_all_tables()
    print(" Tablas creadas.")