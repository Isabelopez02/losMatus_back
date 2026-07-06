from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models
from app.controllers.cliente_controller import cliente_bp
from app.controllers.equipo_controller import equipo_bp
from app.controllers.ticket_controller import ticket_bp
from app.controllers.chat_incidencia_controller import chat_bp
from app.controllers.historial_controller import historial_bp

app = FastAPI(
    title="FastAPI MVC Backend",
    description="FastAPI MVC Backend matching Angular Frontend interfaces",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(cliente_bp, prefix="/api/clientes", tags=["Clientes"])
app.include_router(equipo_bp, prefix="/api/equipos", tags=["Equipos"])
app.include_router(ticket_bp, prefix="/api/tickets", tags=["Tickets"])
app.include_router(chat_bp, prefix="/api/chats", tags=["Chats"])
app.include_router(historial_bp, prefix="/api/historial", tags=["Historial"])

# Auto-create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {
        "message": "FastAPI MVC Backend is running!",
        "status": "success",
        "docs": "/docs"
    }
