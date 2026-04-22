# DTO de salida del login con el JWT devuelto al frontend.
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
