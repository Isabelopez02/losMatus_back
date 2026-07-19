from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TicketBase(BaseModel):
    codigo: str
    descripcion: str
    fecha_reporte: Optional[datetime] = None
    fecha_inicio_atencion: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    fecha_limite_resolucion: Optional[datetime] = None
    cumple_sla: bool = True
    categoria: str
    estado_incidencia: str = 'Abierto'
    severidad: str
    sugerencia_ia: Optional[str] = None
    id_usuario: int
    id_equipo: Optional[int] = None
    id_tecnico: Optional[int] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_reporte: Optional[datetime] = None
    fecha_inicio_atencion: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    fecha_limite_resolucion: Optional[datetime] = None
    cumple_sla: Optional[bool] = None
    categoria: Optional[str] = None
    estado_incidencia: Optional[str] = None
    severidad: Optional[str] = None
    sugerencia_ia: Optional[str] = None
    id_usuario: Optional[int] = None
    id_equipo: Optional[int] = None
    id_tecnico: Optional[int] = None
    id_usuario_accion: Optional[int] = None
    comentarios_historial: Optional[str] = None

class Ticket(TicketBase):
    id_incidencia: int
    cliente_respondio: Optional[bool] = False

    class Config:
        from_attributes = True
