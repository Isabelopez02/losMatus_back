from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Equipo(Base):
    __tablename__ = 'equipos'

    id_equipo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_qr = Column(String(255), unique=True, index=True, nullable=False)
    nombre_equipo = Column(String(100), nullable=False)
    tipo_equipo = Column(String(100), nullable=False)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    ubicacion = Column(String(150), nullable=False)
    estado = Column(String(50), default='Activo', nullable=False)
    id_usuario = Column(Integer, ForeignKey('clientes.id_usuario'), nullable=False)

    # Relationships
    cliente = relationship("Cliente", backref="equipos")
