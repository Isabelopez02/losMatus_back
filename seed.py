from app import create_app
from app.database import db
from app.models.cliente import Cliente
from app.models.equipo import Equipo
from app.models.ticket import Ticket
from app.models.chat_incidencia import ChatIncidencia
from app.models.historial import Historial
from datetime import datetime

def seed():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("Database cleared and schema created successfully.")

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
        db.session.add(cliente)
        db.session.commit()
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
        db.session.add(equipo)
        db.session.commit()
        print(f"Created Equipo: {equipo.nombre_equipo} with id {equipo.id_equipo}")

        # 3. Create Ticket
        ticket = Ticket(
            codigo="TCK-2026-001",
            descripcion="El servidor principal está experimentando alta latencia e intermitencia en el puerto HTTP.",
            fecha_reporte=datetime.utcnow(),
            fecha_limite_resolucion=datetime.utcnow(), # simplified
            cumple_sla=True,
            categoria="Hardware",
            estado_incidencia="Abierto",
            severidad="Alta",
            id_usuario=cliente.id_usuario,
            id_equipo=equipo.id_equipo,
            id_tecnico=None
        )
        db.session.add(ticket)
        db.session.commit()
        print(f"Created Ticket: {ticket.codigo} with id {ticket.id_incidencia}")

        # 4. Create ChatIncidencia
        chat = ChatIncidencia(
            mensaje="Hola, mi servidor está fallando. Adjunto log de errores.",
            tipo_mensaje="texto",
            id_incidencia=ticket.id_incidencia,
            id_usuario=cliente.id_usuario
        )
        db.session.add(chat)
        db.session.commit()
        print(f"Created Chat Log for Ticket {ticket.codigo}")

        # 5. Create Historial (Note: Ticket POST controller does this automatically, but doing it here manually to test Historial)
        historial = Historial(
            accion_realizada="Creación de Ticket",
            estado_anterior="Ninguno",
            estado_nuevo="Abierto",
            id_incidencia=ticket.id_incidencia,
            id_usuario=cliente.id_usuario,
            comentarios="Reportado por el bot de Telegram automáticamente."
        )
        db.session.add(historial)
        db.session.commit()
        print("Created Historial Log entry.")
        print("\nAll model instances seeded successfully! DB is ready for testing.")

if __name__ == '__main__':
    seed()
