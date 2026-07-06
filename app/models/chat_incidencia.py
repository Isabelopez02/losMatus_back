from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ChatIncidencia(Base):
    __tablename__ = 'chat_incidencias'

    id_chat = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_envio = Column(DateTime, default=datetime.utcnow, nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo_mensaje = Column(String(50), nullable=False)
    id_incidencia = Column(Integer, ForeignKey('tickets.id_incidencia'), nullable=False)
    id_usuario = Column(Integer, ForeignKey('clientes.id_usuario'), nullable=False)

    # Relationships
    ticket = relationship("Ticket", backref="chats")
    cliente = relationship("Cliente", backref="chats")
