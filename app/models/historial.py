from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Historial(Base):
    __tablename__ = 'historiales'

    id_historial = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_cambio = Column(DateTime, default=datetime.utcnow, nullable=False)
    accion_realizada = Column(String(150), nullable=False)
    estado_anterior = Column(String(50), nullable=False)
    estado_nuevo = Column(String(50), nullable=False)
    id_incidencia = Column(Integer, ForeignKey('tickets.id_incidencia'), nullable=False)
    id_usuario = Column(Integer, ForeignKey('clientes.id_usuario'), nullable=False)
    comentarios = Column(Text, nullable=True)

    # Relationships
    ticket = relationship("Ticket", backref="historiales")
    cliente = relationship("Cliente", backref="historiales")
