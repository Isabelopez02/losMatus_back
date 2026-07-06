from app.database import db

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    telegram_id = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'apellido_materno': self.apellido_materno,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'activo': self.activo,
            'telegram_id': self.telegram_id
        }
