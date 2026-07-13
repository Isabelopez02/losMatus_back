from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.historial import Historial as HistorialModel
from app.models.ticket import Ticket as TicketModel
from app.models.equipo import Equipo as EquipoModel
from app.models.cliente import Cliente as ClienteModel
from app.schemas.historial import Historial, HistorialCreate

historial_bp = APIRouter()

@historial_bp.get("", response_model=List[Historial])
def get_historiales(db: Session = Depends(get_db)):
    return db.query(HistorialModel).order_by(HistorialModel.fecha_cambio.desc()).all()

@historial_bp.get("/ticket/{id_incidencia}", response_model=List[Historial])
def get_historial_by_ticket(id_incidencia: int, db: Session = Depends(get_db)):
    return db.query(HistorialModel).filter(HistorialModel.id_incidencia == id_incidencia).order_by(HistorialModel.fecha_cambio.desc()).all()

@historial_bp.get("/equipo/{id_equipo}", response_model=List[Historial])
def get_historial_by_equipo(id_equipo: int, db: Session = Depends(get_db)):
    """Trazabilidad del equipo: registros ligados directamente al equipo
    o a través de los tickets asociados a ese equipo."""
    # IDs de tickets que pertenecen a este equipo
    ticket_ids = [t.id_incidencia for t in db.query(TicketModel.id_incidencia).filter(TicketModel.id_equipo == id_equipo).all()]

    query = db.query(HistorialModel).filter(
        (HistorialModel.id_equipo == id_equipo) |
        (HistorialModel.id_incidencia.in_(ticket_ids) if ticket_ids else False)
    )
    return query.order_by(HistorialModel.fecha_cambio.desc()).all()

@historial_bp.post("", response_model=Historial, status_code=status.HTTP_201_CREATED)
def create_historial(historial_data: HistorialCreate, db: Session = Depends(get_db)):
    if not historial_data.id_incidencia and not historial_data.id_equipo:
        raise HTTPException(status_code=400, detail="Debe indicar id_incidencia o id_equipo")

    if historial_data.id_incidencia:
        ticket = db.query(TicketModel).filter(TicketModel.id_incidencia == historial_data.id_incidencia).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket (id_incidencia) not found")

    if historial_data.id_equipo:
        equipo = db.query(EquipoModel).filter(EquipoModel.id_equipo == historial_data.id_equipo).first()
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo (id_equipo) not found")

    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == historial_data.id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente (id_usuario) not found")

    db_data = historial_data.model_dump()
    if not db_data.get('fecha_cambio'):
        db_data['fecha_cambio'] = datetime.utcnow()

    historial = HistorialModel(**db_data)
    db.add(historial)
    db.commit()
    db.refresh(historial)
    return historial
