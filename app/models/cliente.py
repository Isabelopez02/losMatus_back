from sqlalchemy import Column, Integer, String, Text, Boolean, Float
from app.database import Base

class Cliente(Base):
    __tablename__ = 'clientes'

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=True)
    apellido_materno = Column(String(100), nullable=True)
    email = Column(String(150), unique=True, index=True, nullable=True)
    telefono = Column(String(20), nullable=True)
    direccion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    telegram_id = Column(String(50), unique=True, index=True, nullable=True)
    # Ubicación geográfica (la comparte el cliente por Telegram) para Google Maps
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
