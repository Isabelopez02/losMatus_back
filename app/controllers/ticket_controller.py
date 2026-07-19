from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.ticket import Ticket as TicketModel
from app.models.cliente import Cliente as ClienteModel
from app.models.equipo import Equipo as EquipoModel
from app.models.historial import Historial as HistorialModel
from app.schemas.ticket import Ticket, TicketCreate, TicketUpdate
from app.services.ai_service import analizar_incidencia

ticket_bp = APIRouter()

@ticket_bp.get("", response_model=List[Ticket])
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(TicketModel).all()
    from app.models.chat_incidencia import ChatIncidencia as ChatIncidenciaModel
    for t in tickets:
        ultimo_chat = db.query(ChatIncidenciaModel).filter(ChatIncidenciaModel.id_incidencia == t.id_incidencia).order_by(ChatIncidenciaModel.fecha_envio.desc()).first()
        t.cliente_respondio = (ultimo_chat is not None and ultimo_chat.tipo_mensaje != 'tecnico')
    return tickets

@ticket_bp.get("/{id_incidencia}", response_model=Ticket)
def get_ticket(id_incidencia: int, db: Session = Depends(get_db)):
    ticket = db.query(TicketModel).filter(TicketModel.id_incidencia == id_incidencia).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@ticket_bp.post("", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == ticket_data.id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente (id_usuario) not found")
    
    if ticket_data.id_equipo:
        equipo = db.query(EquipoModel).filter(EquipoModel.id_equipo == ticket_data.id_equipo).first()
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo (id_equipo) not found")

    existing = db.query(TicketModel).filter(TicketModel.codigo == ticket_data.codigo).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ticket code already exists")
        
    db_data = ticket_data.model_dump()
    if not db_data.get('fecha_reporte'):
        db_data['fecha_reporte'] = datetime.utcnow()
        
    ticket = TicketModel(**db_data)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    historial = HistorialModel(
        accion_realizada='Creación de Ticket',
        estado_anterior='Ninguno',
        estado_nuevo=ticket.estado_incidencia,
        id_incidencia=ticket.id_incidencia,
        id_usuario=ticket.id_usuario,
        comentarios='Ticket creado a través de la API'
    )
    db.add(historial)
    db.commit()
    
    return ticket

@ticket_bp.post("/{id_incidencia}/analizar", response_model=Ticket)
def analizar_ticket(id_incidencia: int, db: Session = Depends(get_db)):
    """Genera (o regenera) la sugerencia del copiloto IA para el técnico,
    analizando la descripción de la incidencia. Guarda el resultado en el ticket."""
    ticket = db.query(TicketModel).filter(TicketModel.id_incidencia == id_incidencia).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    analisis = analizar_incidencia(ticket.descripcion)
    ticket.sugerencia_ia = analisis.get("sugerencia")
    # Refinamos categoría/severidad con el análisis actual de la IA
    if analisis.get("categoria"):
        ticket.categoria = analisis["categoria"]
    if analisis.get("severidad"):
        ticket.severidad = analisis["severidad"]

    db.commit()
    db.refresh(ticket)
    return ticket

@ticket_bp.put("/{id_incidencia}", response_model=Ticket)
def update_ticket(id_incidencia: int, ticket_data: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(TicketModel).filter(TicketModel.id_incidencia == id_incidencia).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    if ticket_data.id_usuario:
        cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == ticket_data.id_usuario).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente not found")
            
    if ticket_data.id_equipo is not None:
        equipo = db.query(EquipoModel).filter(EquipoModel.id_equipo == ticket_data.id_equipo).first()
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo not found")

    if ticket_data.codigo and ticket_data.codigo != ticket.codigo:
        existing = db.query(TicketModel).filter(TicketModel.codigo == ticket_data.codigo).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ticket code already exists")

    old_estado = ticket.estado_incidencia
    new_estado = ticket_data.estado_incidencia or old_estado
    state_changed = old_estado != new_estado
    
    update_dict = ticket_data.model_dump(exclude_unset=True)
    id_usuario_accion = update_dict.pop('id_usuario_accion', None)
    comentarios_historial = update_dict.pop('comentarios_historial', None)
    
    for key, value in update_dict.items():
        setattr(ticket, key, value)
        
    db.commit()
    db.refresh(ticket)
    
    if state_changed:
        historial = HistorialModel(
            accion_realizada='Cambio de Estado',
            estado_anterior=old_estado,
            estado_nuevo=new_estado,
            id_incidencia=ticket.id_incidencia,
            id_usuario=id_usuario_accion or ticket.id_usuario,
            comentarios=comentarios_historial or f"Estado del ticket actualizado de {old_estado} a {new_estado}"
        )
        db.add(historial)
        db.commit()
        
    return ticket

@ticket_bp.delete("/{id_incidencia}")
def delete_ticket(id_incidencia: int, db: Session = Depends(get_db)):
    ticket = db.query(TicketModel).filter(TicketModel.id_incidencia == id_incidencia).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted successfully", "id_incidencia": id_incidencia}
