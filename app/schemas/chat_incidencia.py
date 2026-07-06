from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatIncidenciaBase(BaseModel):
    fecha_envio: Optional[datetime] = None
    mensaje: str
    tipo_mensaje: str
    id_incidencia: int
    id_usuario: int

class ChatIncidenciaCreate(ChatIncidenciaBase):
    pass

class ChatIncidencia(ChatIncidenciaBase):
    id_chat: int

    class Config:
        from_attributes = True
