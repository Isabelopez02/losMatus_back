from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.cliente import Cliente as ClienteModel
from app.models.ticket import Ticket as TicketModel
from app.schemas.cliente import Cliente, ClienteCreate, ClienteUpdate
from app.schemas.ticket import Ticket

cliente_bp = APIRouter()

@cliente_bp.get("", response_model=List[Cliente])
def get_clientes(db: Session = Depends(get_db)):
    return db.query(ClienteModel).all()

@cliente_bp.get("/{id_usuario}", response_model=Cliente)
def get_cliente(id_usuario: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return cliente

@cliente_bp.get("/telegram/{telegram_id}", response_model=Cliente)
def get_cliente_by_telegram(telegram_id: str, db: Session = Depends(get_db)):
    """Usado por el bot de Telegram para saber si el cliente ya existe."""
    cliente = db.query(ClienteModel).filter(ClienteModel.telegram_id == telegram_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return cliente

@cliente_bp.get("/{id_usuario}/tickets", response_model=List[Ticket])
def get_tickets_by_cliente(id_usuario: int, db: Session = Depends(get_db)):
    """Historial de incidencias (tickets) de un cliente."""
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return db.query(TicketModel).filter(TicketModel.id_usuario == id_usuario).order_by(TicketModel.fecha_reporte.desc()).all()

@cliente_bp.post("", response_model=Cliente, status_code=status.HTTP_201_CREATED)
def create_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    if cliente_data.email:
        existing = db.query(ClienteModel).filter(ClienteModel.email == cliente_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registrado")

    if cliente_data.telegram_id:
        existing_tg = db.query(ClienteModel).filter(ClienteModel.telegram_id == cliente_data.telegram_id).first()
        if existing_tg:
            raise HTTPException(status_code=400, detail="telegram_id already registrado")

    cliente = ClienteModel(**cliente_data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente

@cliente_bp.put("/{id_usuario}", response_model=Cliente)
def update_cliente(id_usuario: int, cliente_data: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")

    update_dict = cliente_data.model_dump(exclude_unset=True)

    new_email = update_dict.get('email')
    if new_email and new_email != cliente.email:
        existing = db.query(ClienteModel).filter(ClienteModel.email == new_email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    for key, value in update_dict.items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente

@cliente_bp.delete("/{id_usuario}")
def delete_cliente(id_usuario: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    # Soft delete
    cliente.activo = False
    db.commit()
    return {"message": "Cliente deactivated successfully", "id_usuario": id_usuario}
