from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Ticket(Base):
    __tablename__ = 'tickets'

    id_incidencia = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    descripcion = Column(Text, nullable=False)
    fecha_reporte = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_inicio_atencion = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)
    fecha_limite_resolucion = Column(DateTime, nullable=True)
    cumple_sla = Column(Boolean, default=True, nullable=False)
    categoria = Column(String(50), nullable=False)
    estado_incidencia = Column(String(50), default='Abierto', nullable=False)
    severidad = Column(String(50), nullable=False)
    id_usuario = Column(Integer, ForeignKey('clientes.id_usuario'), nullable=False)
    id_equipo = Column(Integer, ForeignKey('equipos.id_equipo'), nullable=True)
    id_tecnico = Column(Integer, nullable=True)

    # Relationships
    cliente = relationship("Cliente", backref="tickets")
    equipo = relationship("Equipo", backref="tickets")
