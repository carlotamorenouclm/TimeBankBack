"""
Define esquemas Pydantic para validar entradas y serializar respuestas.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
# DTO de salida del login con el JWT devuelto al frontend.
from pydantic import BaseModel

# Define esta clase y agrupa los datos que pertenecen a la entidad.
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
