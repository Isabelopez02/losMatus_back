from flask import Blueprint, request, jsonify
from app.database import db
from app.models.ticket import Ticket
from app.models.cliente import Cliente
from app.models.equipo import Equipo
from app.models.historial import Historial
from datetime import datetime

ticket_bp = Blueprint('ticket', __name__)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        if date_str.endswith('Z'):
            date_str = date_str.replace('Z', '+00:00')
        return datetime.fromisoformat(date_str)
    except Exception:
        return None

@ticket_bp.route('', methods=['GET'])
def get_tickets():
    tickets = Ticket.query.all()
    return jsonify([t.to_dict() for t in tickets])

@ticket_bp.route('/<int:id_incidencia>', methods=['GET'])
def get_ticket(id_incidencia):
    ticket = Ticket.query.get_or_404(id_incidencia)
    return jsonify(ticket.to_dict())

@ticket_bp.route('', methods=['POST'])
def create_ticket():
    data = request.get_json() or {}
    required = ['codigo', 'descripcion', 'categoria', 'estado_incidencia', 'severidad', 'id_usuario']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Field {field} is required'}), 400

    # Validate foreign keys
    cliente = Cliente.query.get(data['id_usuario'])
    if not cliente:
        return jsonify({'error': 'Cliente (id_usuario) not found'}), 404

    if data.get('id_equipo'):
        equipo = Equipo.query.get(data['id_equipo'])
        if not equipo:
            return jsonify({'error': 'Equipo (id_equipo) not found'}), 404

    # Unique code check
    if Ticket.query.filter_by(codigo=data['codigo']).first():
        return jsonify({'error': f"Ticket code '{data['codigo']}' already exists"}), 400

    ticket = Ticket(
        codigo=data['codigo'],
        descripcion=data['descripcion'],
        fecha_reporte=parse_date(data.get('fecha_reporte')) or datetime.utcnow(),
        fecha_inicio_atencion=parse_date(data.get('fecha_inicio_atencion')),
        fecha_finalizacion=parse_date(data.get('fecha_finalizacion')),
        fecha_limite_resolucion=parse_date(data.get('fecha_limite_resolucion')),
        cumple_sla=data.get('cumple_sla', True),
        categoria=data['categoria'],
        estado_incidencia=data['estado_incidencia'],
        severidad=data['severidad'],
        id_usuario=data['id_usuario'],
        id_equipo=data.get('id_equipo'),
        id_tecnico=data.get('id_tecnico')
    )

    db.session.add(ticket)
    db.session.commit()

    # Automatically write to Historial on creation
    historial = Historial(
        accion_realizada='Creación de Ticket',
        estado_anterior='Ninguno',
        estado_nuevo=ticket.estado_incidencia,
        id_incidencia=ticket.id_incidencia,
        id_usuario=ticket.id_usuario,
        comentarios='Ticket creado a través de la API'
    )
    db.session.add(historial)
    db.session.commit()

    return jsonify(ticket.to_dict()), 201

@ticket_bp.route('/<int:id_incidencia>', methods=['PUT'])
def update_ticket(id_incidencia):
    ticket = Ticket.query.get_or_404(id_incidencia)
    data = request.get_json() or {}

    # Validate foreign keys if they are being updated
    if 'id_usuario' in data:
        cliente = Cliente.query.get(data['id_usuario'])
        if not cliente:
            return jsonify({'error': 'Cliente (id_usuario) not found'}), 404
        ticket.id_usuario = data['id_usuario']

    if 'id_equipo' in data and data['id_equipo'] is not None:
        equipo = Equipo.query.get(data['id_equipo'])
        if not equipo:
            return jsonify({'error': 'Equipo (id_equipo) not found'}), 404
        ticket.id_equipo = data['id_equipo']
    elif 'id_equipo' in data and data['id_equipo'] is None:
        ticket.id_equipo = None

    if 'codigo' in data and data['codigo'] != ticket.codigo:
        if Ticket.query.filter_by(codigo=data['codigo']).first():
            return jsonify({'error': f"Ticket code '{data['codigo']}' already exists"}), 400
        ticket.codigo = data['codigo']

    # Keep track of state transitions to log in Historial
    old_estado = ticket.estado_incidencia
    new_estado = data.get('estado_incidencia', old_estado)
    state_changed = old_estado != new_estado

    ticket.descripcion = data.get('descripcion', ticket.descripcion)
    if 'fecha_reporte' in data:
        ticket.fecha_reporte = parse_date(data['fecha_reporte']) or ticket.fecha_reporte
    if 'fecha_inicio_atencion' in data:
        ticket.fecha_inicio_atencion = parse_date(data['fecha_inicio_atencion'])
    if 'fecha_finalizacion' in data:
        ticket.fecha_finalizacion = parse_date(data['fecha_finalizacion'])
    if 'fecha_limite_resolucion' in data:
        ticket.fecha_limite_resolucion = parse_date(data['fecha_limite_resolucion'])

    ticket.cumple_sla = data.get('cumple_sla', ticket.cumple_sla)
    ticket.categoria = data.get('categoria', ticket.categoria)
    ticket.estado_incidencia = new_estado
    ticket.severidad = data.get('severidad', ticket.severidad)
    ticket.id_tecnico = data.get('id_tecnico', ticket.id_tecnico)

    db.session.commit()

    if state_changed:
        # Automatically log status changes to Historial
        historial = Historial(
            accion_realizada='Cambio de Estado',
            estado_anterior=old_estado,
            estado_nuevo=new_estado,
            id_incidencia=ticket.id_incidencia,
            id_usuario=data.get('id_usuario_accion') or ticket.id_usuario, # User performing the action
            comentarios=data.get('comentarios_historial') or f"Estado del ticket actualizado de {old_estado} a {new_estado}"
        )
        db.session.add(historial)
        db.session.commit()

    return jsonify(ticket.to_dict())

@ticket_bp.route('/<int:id_incidencia>', methods=['DELETE'])
def delete_ticket(id_incidencia):
    ticket = Ticket.query.get_or_404(id_incidencia)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': 'Ticket deleted successfully', 'id_incidencia': id_incidencia})
