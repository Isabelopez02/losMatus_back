from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.cliente import Cliente
from app.models.equipo import Equipo
from app.models.ticket import Ticket
from app.models.chat_incidencia import ChatIncidencia
from app.models.historial import Historial
from datetime import datetime

def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database cleared and schema created successfully.")

    db: Session = SessionLocal()
    try:
        # 1. Create Cliente
        cliente = Cliente(
            nombre="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            email="juan.perez@example.com",
            telefono="+51999999999",
            direccion="Av. Siempreviva 742, Lima",
            activo=True,
            telegram_id="123456789"
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        print(f"Created Cliente: {cliente.nombre} with id {cliente.id_usuario}")

        # 2. Create Equipo
        equipo = Equipo(
            codigo_qr="QR-EQ-001-XYZ",
            nombre_equipo="Servidor Principal",
            tipo_equipo="Servidor Rack",
            marca="Dell",
            modelo="PowerEdge R740",
            ubicacion="Data Center - Rack 3",
            estado="Activo",
            id_usuario=cliente.id_usuario
        )
        db.add(equipo)
        db.commit()
        db.refresh(equipo)
        print(f"Created Equipo: {equipo.nombre_equipo} with id {equipo.id_equipo}")

        # 3. Create Ticket
        ticket = Ticket(
            codigo="TCK-2026-001",
            descripcion="El servidor principal está experimentando alta latencia e intermitencia en el puerto HTTP.",
            fecha_reporte=datetime.utcnow(),
            fecha_limite_resolucion=datetime.utcnow(),
            cumple_sla=True,
            categoria="Hardware",
            estado_incidencia="Abierto",
            severidad="Alta",
            id_usuario=cliente.id_usuario,
            id_equipo=equipo.id_equipo,
            id_tecnico=None
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        print(f"Created Ticket: {ticket.codigo} with id {ticket.id_incidencia}")

        # 4. Create ChatIncidencia
        chat = ChatIncidencia(
            mensaje="Hola, mi servidor está fallando. Adjunto log de errores.",
            tipo_mensaje="texto",
            id_incidencia=ticket.id_incidencia,
            id_usuario=cliente.id_usuario
        )
        db.add(chat)
        db.commit()
        print(f"Created Chat Log for Ticket {ticket.codigo}")

        # 5. Create Historial
        historial = Historial(
            accion_realizada="Creación de Ticket",
            estado_anterior="Ninguno",
            estado_nuevo="Abierto",
            id_incidencia=ticket.id_incidencia,
            id_usuario=cliente.id_usuario,
            comentarios="Reportado por el bot de Telegram automáticamente."
        )
        db.add(historial)
        db.commit()
        print("Created Historial Log entry.")
        print("\nAll model instances seeded successfully! DB is ready for testing.")
    finally:
        db.close()

if __name__ == '__main__':
    seed()
