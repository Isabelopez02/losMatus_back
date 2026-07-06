from flask import Blueprint, request, jsonify
from app.database import db
from app.models.historial import Historial
from app.models.ticket import Ticket
from app.models.cliente import Cliente
from datetime import datetime

historial_bp = Blueprint('historial', __name__)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        if date_str.endswith('Z'):
            date_str = date_str.replace('Z', '+00:00')
        return datetime.fromisoformat(date_str)
    except Exception:
        return None

@historial_bp.route('', methods=['GET'])
def get_historiales():
    historiales = Historial.query.all()
    return jsonify([h.to_dict() for h in historiales])

@historial_bp.route('/ticket/<int:id_incidencia>', methods=['GET'])
def get_historial_by_ticket(id_incidencia):
    historiales = Historial.query.filter_by(id_incidencia=id_incidencia).order_by(Historial.fecha_cambio.desc()).all()
    return jsonify([h.to_dict() for h in historiales])

@historial_bp.route('', methods=['POST'])
def create_historial():
    data = request.get_json() or {}
    required = ['accion_realizada', 'estado_anterior', 'estado_nuevo', 'id_incidencia', 'id_usuario']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Field {field} is required'}), 400

    # Validate foreign keys
    ticket = Ticket.query.get(data['id_incidencia'])
    if not ticket:
        return jsonify({'error': 'Ticket (id_incidencia) not found'}), 404

    cliente = Cliente.query.get(data['id_usuario'])
    if not cliente:
        return jsonify({'error': 'Cliente (id_usuario) not found'}), 404

    historial = Historial(
        fecha_cambio=parse_date(data.get('fecha_cambio')) or datetime.utcnow(),
        accion_realizada=data['accion_realizada'],
        estado_anterior=data['estado_anterior'],
        estado_nuevo=data['estado_nuevo'],
        id_incidencia=data['id_incidencia'],
        id_usuario=data['id_usuario'],
        comentarios=data.get('comentarios')
    )
    db.session.add(historial)
    db.session.commit()
    return jsonify(historial.to_dict()), 201
