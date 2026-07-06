from app.database import db
from datetime import datetime

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id_incidencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_inicio_atencion = db.Column(db.DateTime, nullable=True)
    fecha_finalizacion = db.Column(db.DateTime, nullable=True)
    fecha_limite_resolucion = db.Column(db.DateTime, nullable=True)
    cumple_sla = db.Column(db.Boolean, default=True, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    estado_incidencia = db.Column(db.String(50), default='Abierto', nullable=False)
    severidad = db.Column(db.String(50), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('clientes.id_usuario'), nullable=False)
    id_equipo = db.Column(db.Integer, db.ForeignKey('equipos.id_equipo'), nullable=True)
    id_tecnico = db.Column(db.Integer, nullable=True)

    # Relationships
    cliente = db.relationship('Cliente', backref=db.backref('tickets', lazy=True))
    equipo = db.relationship('Equipo', backref=db.backref('tickets', lazy=True))

    def to_dict(self):
        return {
            'id_incidencia': self.id_incidencia,
            'codigo': self.codigo,
            'descripcion': self.descripcion,
            'fecha_reporte': self.fecha_reporte.isoformat() if self.fecha_reporte else None,
            'fecha_inicio_atencion': self.fecha_inicio_atencion.isoformat() if self.fecha_inicio_atencion else None,
            'fecha_finalizacion': self.fecha_finalizacion.isoformat() if self.fecha_finalizacion else None,
            'fecha_limite_resolucion': self.fecha_limite_resolucion.isoformat() if self.fecha_limite_resolucion else None,
            'cumple_sla': self.cumple_sla,
            'categoria': self.categoria,
            'estado_incidencia': self.estado_incidencia,
            'severidad': self.severidad,
            'id_usuario': self.id_usuario,
            'id_equipo': self.id_equipo,
            'id_tecnico': self.id_tecnico
        }
