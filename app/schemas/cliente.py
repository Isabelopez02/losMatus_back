from pydantic import BaseModel
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool = True
    telegram_id: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None
    telegram_id: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class Cliente(ClienteBase):
    id_usuario: int

    class Config:
        from_attributes = True
