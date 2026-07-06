from sqlalchemy import Column, Integer, String, Text, Boolean
from app.database import Base

class Cliente(Base):
    __tablename__ = 'clientes'

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=False)
    apellido_materno = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    telefono = Column(String(20), nullable=False)
    direccion = Column(Text, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    telegram_id = Column(String(50), nullable=True)
