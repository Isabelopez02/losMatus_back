from flask import Blueprint, request, jsonify
from app.database import db
from app.models.chat_incidencia import ChatIncidencia
from app.models.ticket import Ticket
from app.models.cliente import Cliente
from datetime import datetime

chat_bp = Blueprint('chat_incidencia', __name__)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        if date_str.endswith('Z'):
            date_str = date_str.replace('Z', '+00:00')
        return datetime.fromisoformat(date_str)
    except Exception:
        return None

@chat_bp.route('', methods=['GET'])
def get_chats():
    chats = ChatIncidencia.query.all()
    return jsonify([c.to_dict() for c in chats])

@chat_bp.route('/ticket/<int:id_incidencia>', methods=['GET'])
def get_chats_by_ticket(id_incidencia):
    chats = ChatIncidencia.query.filter_by(id_incidencia=id_incidencia).order_by(ChatIncidencia.fecha_envio.asc()).all()
    return jsonify([c.to_dict() for c in chats])

@chat_bp.route('', methods=['POST'])
def create_chat():
    data = request.get_json() or {}
    required = ['mensaje', 'tipo_mensaje', 'id_incidencia', 'id_usuario']
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

    chat = ChatIncidencia(
        fecha_envio=parse_date(data.get('fecha_envio')) or datetime.utcnow(),
        mensaje=data['mensaje'],
        tipo_mensaje=data['tipo_mensaje'],
        id_incidencia=data['id_incidencia'],
        id_usuario=data['id_usuario']
    )
    db.session.add(chat)
    db.session.commit()
    return jsonify(chat.to_dict()), 201
