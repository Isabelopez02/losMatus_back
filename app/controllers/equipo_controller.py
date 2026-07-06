from flask import Blueprint, request, jsonify
from app.database import db
from app.models.equipo import Equipo
from app.models.cliente import Cliente

equipo_bp = Blueprint('equipo', __name__)

@equipo_bp.route('', methods=['GET'])
def get_equipos():
    equipos = Equipo.query.all()
    return jsonify([e.to_dict() for e in equipos])

@equipo_bp.route('/<int:id_equipo>', methods=['GET'])
def get_equipo(id_equipo):
    equipo = Equipo.query.get_or_404(id_equipo)
    return jsonify(equipo.to_dict())

@equipo_bp.route('/qr/<string:codigo_qr>', methods=['GET'])
def get_equipo_by_qr(codigo_qr):
    equipo = Equipo.query.filter_by(codigo_qr=codigo_qr).first_or_404()
    return jsonify(equipo.to_dict())

@equipo_bp.route('', methods=['POST'])
def create_equipo():
    data = request.get_json() or {}
    required = ['codigo_qr', 'nombre_equipo', 'tipo_equipo', 'marca', 'modelo', 'ubicacion', 'id_usuario']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Field {field} is required'}), 400

    # Verify user exists
    cliente = Cliente.query.get(data['id_usuario'])
    if not cliente:
        return jsonify({'error': 'Cliente (id_usuario) not found'}), 404

    # Verify QR code is unique
    if Equipo.query.filter_by(codigo_qr=data['codigo_qr']).first():
        return jsonify({'error': 'QR code already exists'}), 400

    equipo = Equipo(
        codigo_qr=data['codigo_qr'],
        nombre_equipo=data['nombre_equipo'],
        tipo_equipo=data['tipo_equipo'],
        marca=data['marca'],
        modelo=data['modelo'],
        ubicacion=data['ubicacion'],
        estado=data.get('estado', 'Activo'),
        id_usuario=data['id_usuario']
    )
    db.session.add(equipo)
    db.session.commit()
    return jsonify(equipo.to_dict()), 201

@equipo_bp.route('/<int:id_equipo>', methods=['PUT'])
def update_equipo(id_equipo):
    equipo = Equipo.query.get_or_404(id_equipo)
    data = request.get_json() or {}

    if 'id_usuario' in data:
        cliente = Cliente.query.get(data['id_usuario'])
        if not cliente:
            return jsonify({'error': 'Cliente (id_usuario) not found'}), 404
        equipo.id_usuario = data['id_usuario']

    if 'codigo_qr' in data and data['codigo_qr'] != equipo.codigo_qr:
        if Equipo.query.filter_by(codigo_qr=data['codigo_qr']).first():
            return jsonify({'error': 'QR code already exists'}), 400
        equipo.codigo_qr = data['codigo_qr']

    equipo.nombre_equipo = data.get('nombre_equipo', equipo.nombre_equipo)
    equipo.tipo_equipo = data.get('tipo_equipo', equipo.tipo_equipo)
    equipo.marca = data.get('marca', equipo.marca)
    equipo.modelo = data.get('modelo', equipo.modelo)
    equipo.ubicacion = data.get('ubicacion', equipo.ubicacion)
    equipo.estado = data.get('estado', equipo.estado)

    db.session.commit()
    return jsonify(equipo.to_dict())

@equipo_bp.route('/<int:id_equipo>', methods=['DELETE'])
def delete_equipo(id_equipo):
    equipo = Equipo.query.get_or_404(id_equipo)
    db.session.delete(equipo)
    db.session.commit()
    return jsonify({'message': 'Equipo deleted successfully', 'id_equipo': id_equipo})
