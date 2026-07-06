from pydantic import BaseModel
from typing import Optional

class EquipoBase(BaseModel):
    codigo_qr: str
    nombre_equipo: str
    tipo_equipo: str
    marca: str
    modelo: str
    ubicacion: str
    estado: str = 'Activo'
    id_usuario: int

class EquipoCreate(EquipoBase):
    pass

class Equipo(EquipoBase):
    id_equipo: int

    class Config:
        from_attributes = True
