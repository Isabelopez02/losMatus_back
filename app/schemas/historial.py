from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HistorialBase(BaseModel):
    fecha_cambio: Optional[datetime] = None
    accion_realizada: str
    estado_anterior: str
    estado_nuevo: str
    id_incidencia: Optional[int] = None
    id_equipo: Optional[int] = None
    id_usuario: int
    comentarios: Optional[str] = None

class HistorialCreate(HistorialBase):
    pass

class Historial(HistorialBase):
    id_historial: int

    class Config:
        from_attributes = True
