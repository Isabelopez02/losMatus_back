from flask import Blueprint, request, jsonify
from app.database import db
from app.models.cliente import Cliente

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('', methods=['GET'])
def get_clientes():
    clientes = Cliente.query.all()
    return jsonify([c.to_dict() for c in clientes])

@cliente_bp.route('/<int:id_usuario>', methods=['GET'])
def get_cliente(id_usuario):
    cliente = Cliente.query.get_or_404(id_usuario)
    return jsonify(cliente.to_dict())

@cliente_bp.route('', methods=['POST'])
def create_cliente():
    data = request.get_json() or {}
    required = ['nombre', 'apellido_paterno', 'apellido_materno', 'email', 'telefono', 'direccion']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Field {field} is required'}), 400

    if Cliente.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    cliente = Cliente(
        nombre=data['nombre'],
        apellido_paterno=data['apellido_paterno'],
        apellido_materno=data['apellido_materno'],
        email=data['email'],
        telefono=data['telefono'],
        direccion=data['direccion'],
        activo=data.get('activo', True),
        telegram_id=data.get('telegram_id')
    )
    db.session.add(cliente)
    db.session.commit()
    return jsonify(cliente.to_dict()), 201

@cliente_bp.route('/<int:id_usuario>', methods=['PUT'])
def update_cliente(id_usuario):
    cliente = Cliente.query.get_or_404(id_usuario)
    data = request.get_json() or {}

    if 'email' in data and data['email'] != cliente.email:
        if Cliente.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        cliente.email = data['email']

    cliente.nombre = data.get('nombre', cliente.nombre)
    cliente.apellido_paterno = data.get('apellido_paterno', cliente.apellido_paterno)
    cliente.apellido_materno = data.get('apellido_materno', cliente.apellido_materno)
    cliente.telefono = data.get('telefono', cliente.telefono)
    cliente.direccion = data.get('direccion', cliente.direccion)
    cliente.activo = data.get('activo', cliente.activo)
    cliente.telegram_id = data.get('telegram_id', cliente.telegram_id)

    db.session.commit()
    return jsonify(cliente.to_dict())

@cliente_bp.route('/<int:id_usuario>', methods=['DELETE'])
def delete_cliente(id_usuario):
    cliente = Cliente.query.get_or_404(id_usuario)
    # Instead of hard-delete, we can soft-delete by deactivating
    cliente.activo = False
    db.session.commit()
    return jsonify({'message': 'Cliente deactivated successfully', 'id_usuario': id_usuario})
