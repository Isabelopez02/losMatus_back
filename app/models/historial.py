from app.database import db
from datetime import datetime

class Historial(db.Model):
    __tablename__ = 'historiales'

    id_historial = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    accion_realizada = db.Column(db.String(150), nullable=False)
    estado_anterior = db.Column(db.String(50), nullable=False)
    estado_nuevo = db.Column(db.String(50), nullable=False)
    id_incidencia = db.Column(db.Integer, db.ForeignKey('tickets.id_incidencia'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('clientes.id_usuario'), nullable=False)
    comentarios = db.Column(db.Text, nullable=True)

    # Relationships
    ticket = db.relationship('Ticket', backref=db.backref('historiales', lazy=True))
    cliente = db.relationship('Cliente', backref=db.backref('historiales', lazy=True))

    def to_dict(self):
        return {
            'id_historial': self.id_historial,
            'fecha_cambio': self.fecha_cambio.isoformat() if self.fecha_cambio else None,
            'accion_realizada': self.accion_realizada,
            'estado_anterior': self.estado_anterior,
            'estado_nuevo': self.estado_nuevo,
            'id_incidencia': self.id_incidencia,
            'id_usuario': self.id_usuario,
            'comentarios': self.comentarios
        }
