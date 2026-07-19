from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.chat_incidencia import ChatIncidencia as ChatIncidenciaModel
from app.models.ticket import Ticket as TicketModel
from app.models.cliente import Cliente as ClienteModel
from app.schemas.chat_incidencia import ChatIncidencia, ChatIncidenciaCreate

chat_bp = APIRouter()

@chat_bp.get("", response_model=List[ChatIncidencia])
def get_chats(db: Session = Depends(get_db)):
    return db.query(ChatIncidenciaModel).all()

@chat_bp.get("/ticket/{id_incidencia}", response_model=List[ChatIncidencia])
def get_chats_by_ticket(id_incidencia: int, db: Session = Depends(get_db)):
    return db.query(ChatIncidenciaModel).filter(ChatIncidenciaModel.id_incidencia == id_incidencia).order_by(ChatIncidenciaModel.fecha_envio.asc()).all()

@chat_bp.post("", response_model=ChatIncidencia, status_code=status.HTTP_201_CREATED)
def create_chat(chat_data: ChatIncidenciaCreate, db: Session = Depends(get_db)):
    ticket = db.query(TicketModel).filter(TicketModel.id_incidencia == chat_data.id_incidencia).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket (id_incidencia) not found")
        
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == chat_data.id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente (id_usuario) not found")
        
    db_data = chat_data.model_dump()
    if not db_data.get('fecha_envio'):
        db_data['fecha_envio'] = datetime.utcnow()
        
    chat = ChatIncidenciaModel(**db_data)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


from pydantic import BaseModel
import requests
from app.config import settings

class MensajeEnviar(BaseModel):
    id_incidencia: int
    id_usuario: int
    mensaje: str

@chat_bp.post("/enviar", response_model=ChatIncidencia, status_code=status.HTTP_201_CREATED)
def enviar_mensaje_telegram(datos: MensajeEnviar, db: Session = Depends(get_db)):
    # 1. Obtener cliente para sacar su telegram_id
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == datos.id_usuario).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
        
    if not cliente.telegram_id:
        raise HTTPException(status_code=400, detail="El cliente no tiene un ID de Telegram registrado")

    # 2. Enviar por Telegram
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": cliente.telegram_id,
        "text": f"👨‍🔧 *Técnico de Los Matus:*\n{datos.mensaje}",
        "parse_mode": "Markdown"
    }
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando mensaje a Telegram: {str(e)}")

    # 3. Guardar en base de datos
    chat = ChatIncidenciaModel(
        fecha_envio=datetime.utcnow(),
        mensaje=datos.mensaje,
        tipo_mensaje="tecnico",
        id_incidencia=datos.id_incidencia,
        id_usuario=datos.id_usuario
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    
    return chat

