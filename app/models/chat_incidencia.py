from app.database import db
from datetime import datetime

class ChatIncidencia(db.Model):
    __tablename__ = 'chat_incidencias'

    id_chat = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tipo_mensaje = db.Column(db.String(50), nullable=False)
    id_incidencia = db.Column(db.Integer, db.ForeignKey('tickets.id_incidencia'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('clientes.id_usuario'), nullable=False)

    # Relationships
    ticket = db.relationship('Ticket', backref=db.backref('chats', lazy=True))
    cliente = db.relationship('Cliente', backref=db.backref('chats', lazy=True))

    def to_dict(self):
        return {
            'id_chat': self.id_chat,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None,
            'mensaje': self.mensaje,
            'tipo_mensaje': self.tipo_mensaje,
            'id_incidencia': self.id_incidencia,
            'id_usuario': self.id_usuario
        }
