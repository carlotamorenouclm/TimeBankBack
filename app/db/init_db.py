"""
Encapsula consultas y acceso a base de datos para mantener limpias las rutas.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
# Helper script to create or drop tables manually outside normal startup.
from app.db.session import engine
from app.models.users import Base  # noqa: F401
from app.models.users import User  # noqa: F401
from app.models.chat import ChatMessage  # noqa: F401
from app.models.portal import ServiceOffer  # noqa: F401
from app.models.portal import ServiceRequest  # noqa: F401
from app.models.portal import TransactionReview  # noqa: F401
from app.models.portal import UserTransaction  # noqa: F401
from app.models.portal import UserWallet  # noqa: F401
from app.models.portal import WalletRecharge  # noqa: F401


# Crea o registra el recurso solicitado y prepara la respuesta.
def create_all_tables():
    Base.metadata.create_all(bind=engine)


# Encapsula una parte concreta de la logica de la aplicacion.
def drop_all_tables():
    Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    create_all_tables()
    print(" Tables created.")
