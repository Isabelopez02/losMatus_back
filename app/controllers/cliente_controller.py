from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.cliente import Cliente as ClienteModel
from app.schemas.cliente import Cliente, ClienteCreate

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

@cliente_bp.post("", response_model=Cliente, status_code=status.HTTP_201_CREATED)
def create_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    existing = db.query(ClienteModel).filter(ClienteModel.email == cliente_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registrado")
    
    cliente = ClienteModel(**cliente_data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente

@cliente_bp.put("/{id_usuario}", response_model=Cliente)
def update_cliente(id_usuario: int, cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    
    if cliente_data.email != cliente.email:
        existing = db.query(ClienteModel).filter(ClienteModel.email == cliente_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    for key, value in cliente_data.model_dump().items():
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
