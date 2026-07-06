from pydantic import BaseModel
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    email: str
    telefono: str
    direccion: str
    activo: bool = True
    telegram_id: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id_usuario: int

    class Config:
        from_attributes = True
