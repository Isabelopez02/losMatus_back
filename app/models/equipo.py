from app.database import db

class Equipo(db.Model):
    __tablename__ = 'equipos'

    id_equipo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo_qr = db.Column(db.String(255), unique=True, nullable=False)
    nombre_equipo = db.Column(db.String(100), nullable=False)
    tipo_equipo = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.String(50), default='Activo', nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('clientes.id_usuario'), nullable=False)

    # Relationship
    cliente = db.relationship('Cliente', backref=db.backref('equipos', lazy=True))

    def to_dict(self):
        return {
            'id_equipo': self.id_equipo,
            'codigo_qr': self.codigo_qr,
            'nombre_equipo': self.nombre_equipo,
            'tipo_equipo': self.tipo_equipo,
            'marca': self.marca,
            'modelo': self.modelo,
            'ubicacion': self.ubicacion,
            'estado': self.estado,
            'id_usuario': self.id_usuario
        }
