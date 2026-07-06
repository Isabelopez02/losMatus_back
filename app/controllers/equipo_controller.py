from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.equipo import Equipo as EquipoModel
from app.models.cliente import Cliente as ClienteModel
from app.schemas.equipo import Equipo, EquipoCreate

equipo_bp = APIRouter()

@equipo_bp.get("", response_model=List[Equipo])
def get_equipos(db: Session = Depends(get_db)):
    return db.query(EquipoModel).all()

@equipo_bp.get("/{id_equipo}", response_model=Equipo)
def get_equipo(id_equipo: int, db: Session = Depends(get_db)):
    equipo = db.query(EquipoModel).filter(EquipoModel.id_equipo == id_equipo).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo not found")
    return equipo

@equipo_bp.get("/qr/{codigo_qr}", response_model=Equipo)
def get_equipo_by_qr(codigo_qr: str, db: Session = Depends(get_db)):
    equipo = db.query(EquipoModel).filter(EquipoModel.codigo_qr == codigo_qr).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo with specified QR code not found")
    return equipo

@equipo_bp.post("", response_model=Equipo, status_code=status.HTTP_201_CREATED)
def create_equipo(equipo_data: EquipoCreate, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == equipo_data.id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente (id_usuario) not found")
    
    existing = db.query(EquipoModel).filter(EquipoModel.codigo_qr == equipo_data.codigo_qr).first()
    if existing:
        raise HTTPException(status_code=400, detail="QR code already exists")
        
    equipo = EquipoModel(**equipo_data.model_dump())
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo

@equipo_bp.put("/{id_equipo}", response_model=Equipo)
def update_equipo(id_equipo: int, equipo_data: EquipoCreate, db: Session = Depends(get_db)):
    equipo = db.query(EquipoModel).filter(EquipoModel.id_equipo == id_equipo).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo not found")
        
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == equipo_data.id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente (id_usuario) not found")
        
    if equipo_data.codigo_qr != equipo.codigo_qr:
        existing = db.query(EquipoModel).filter(EquipoModel.codigo_qr == equipo_data.codigo_qr).first()
        if existing:
            raise HTTPException(status_code=400, detail="QR code already exists")
            
    for key, value in equipo_data.model_dump().items():
        setattr(equipo, key, value)
        
    db.commit()
    db.refresh(equipo)
    return equipo

@equipo_bp.delete("/{id_equipo}")
def delete_equipo(id_equipo: int, db: Session = Depends(get_db)):
    equipo = db.query(EquipoModel).filter(EquipoModel.id_equipo == id_equipo).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo not found")
    db.delete(equipo)
    db.commit()
    return {"message": "Equipo deleted successfully", "id_equipo": id_equipo}
