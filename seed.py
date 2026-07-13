from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.cliente import Cliente
from app.models.equipo import Equipo
from app.models.ticket import Ticket
from app.models.chat_incidencia import ChatIncidencia
from app.models.historial import Historial
from datetime import datetime


def seed():
    """Reinicia el esquema y carga datos de demostración coherentes con el frontend."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Base de datos reiniciada y esquema creado correctamente.")

    db: Session = SessionLocal()
    try:
        # ==========================================
        # 1. CLIENTES
        # ==========================================
        clientes = [
            Cliente(nombre="Isabel", apellido_paterno="Matus", apellido_materno="Díaz",
                    email="isabel@matus.com", telefono="+56912345678",
                    direccion="Av. Providencia 1200, Santiago", activo=True, telegram_id="isabel_matus",
                    latitud=-33.4263, longitud=-70.6200),
            Cliente(nombre="Carlos", apellido_paterno="Pérez", apellido_materno="Gómez",
                    email="carlos.perez@gmail.com", telefono="+56987654321",
                    direccion="Las Condes 340, Santiago", activo=True,
                    latitud=-33.4089, longitud=-70.5710),
            Cliente(nombre="Roberto", apellido_paterno="Soto", apellido_materno="Muñoz",
                    email="roberto@soto.cl", telefono="+56955566677",
                    direccion="Vitacura 9821, Santiago", activo=True,
                    latitud=-33.3900, longitud=-70.5730),
        ]
        db.add_all(clientes)
        db.commit()
        for c in clientes:
            db.refresh(c)
        print(f"Creados {len(clientes)} clientes.")

        isabel, carlos, _roberto = clientes

        # ==========================================
        # 2. EQUIPOS
        # ==========================================
        equipos = [
            Equipo(codigo_qr="QR-CAM-CCTV-001", nombre_equipo="Cámara Exterior Bullet 4K",
                   tipo_equipo="Cámara", marca="Hikvision", modelo="DS-2CD2087G2",
                   ubicacion="Entrada Principal - Patio", estado="Activo", id_usuario=isabel.id_usuario),
            Equipo(codigo_qr="QR-BIO-LCT-002", nombre_equipo="Lector Biométrico Huella",
                   tipo_equipo="Lector", marca="ZKTeco", modelo="F22",
                   ubicacion="Puerta Oficinas Piso 2", estado="Activo", id_usuario=carlos.id_usuario),
            Equipo(codigo_qr="QR-DVR-REC-003", nombre_equipo="DVR Grabador 16 Canales",
                   tipo_equipo="Grabador DVR", marca="Dahua", modelo="XVR5116H",
                   ubicacion="Rack de Telecomunicaciones", estado="Activo", id_usuario=isabel.id_usuario),
        ]
        db.add_all(equipos)
        db.commit()
        for e in equipos:
            db.refresh(e)
        print(f"Creados {len(equipos)} equipos.")

        cam, biometrico, dvr = equipos

        # ==========================================
        # 3. TICKETS (Incidencias)
        # ==========================================
        tickets = [
            Ticket(codigo="TCK-9281",
                   descripcion="La pantalla del equipo de CCTV no enciende y emite un pitido constante.",
                   fecha_reporte=datetime.utcnow(), cumple_sla=True, categoria="Hardware",
                   estado_incidencia="Abierto", severidad="Alta",
                   id_usuario=isabel.id_usuario, id_equipo=cam.id_equipo),
            Ticket(codigo="TCK-4829",
                   descripcion="Actualización de firmware solicitada para el lector biométrico.",
                   fecha_reporte=datetime.utcnow(), cumple_sla=True, categoria="Software",
                   estado_incidencia="En Proceso", severidad="Media",
                   id_usuario=carlos.id_usuario, id_equipo=biometrico.id_equipo, id_tecnico=12),
            Ticket(codigo="TCK-1102",
                   descripcion="Cámara de entrada principal no graba, pantalla en negro en el DVR.",
                   fecha_reporte=datetime.utcnow(), cumple_sla=True, categoria="Hardware",
                   estado_incidencia="Abierto", severidad="Crítica",
                   id_usuario=isabel.id_usuario, id_equipo=dvr.id_equipo),
        ]
        db.add_all(tickets)
        db.commit()
        for t in tickets:
            db.refresh(t)
        print(f"Creados {len(tickets)} tickets.")

        ticket_cam = tickets[0]

        # ==========================================
        # 4. CHAT DE INCIDENCIA (log de Telegram)
        # ==========================================
        chat = ChatIncidencia(
            mensaje="Hola, la cámara de la entrada no enciende y hace un pitido. Adjunto foto.",
            tipo_mensaje="texto",
            id_incidencia=ticket_cam.id_incidencia,
            id_usuario=isabel.id_usuario,
        )
        db.add(chat)
        db.commit()
        print("Creado log de chat para el primer ticket.")

        # ==========================================
        # 5. HISTORIAL (Trazabilidad)
        # ==========================================
        historiales = [
            Historial(accion_realizada="Instalación de Equipo y Puesta en Marcha",
                      estado_anterior="Nuevo", estado_nuevo="Activo",
                      id_equipo=cam.id_equipo, id_usuario=isabel.id_usuario,
                      comentarios="Se fijó soporte en muro exterior, cableado UTP Cat6 e inyección PoE probada."),
            Historial(accion_realizada="Mantenimiento Preventivo Bimestral",
                      estado_anterior="Activo", estado_nuevo="Activo",
                      id_equipo=cam.id_equipo, id_usuario=isabel.id_usuario,
                      comentarios="Limpieza de lente exterior y ajuste de ángulo de visión nocturna."),
            Historial(accion_realizada="Reemplazo de Conector RJ45",
                      estado_anterior="En Mantenimiento", estado_nuevo="Activo",
                      id_equipo=dvr.id_equipo, id_usuario=isabel.id_usuario,
                      comentarios="Se crimpó nuevo conector y se selló con cinta autofundente por humedad."),
            Historial(accion_realizada="Creación de Ticket",
                      estado_anterior="Ninguno", estado_nuevo="Abierto",
                      id_incidencia=ticket_cam.id_incidencia, id_equipo=cam.id_equipo,
                      id_usuario=isabel.id_usuario,
                      comentarios="Reportado por el bot de Telegram automáticamente."),
        ]
        db.add_all(historiales)
        db.commit()
        print(f"Creados {len(historiales)} registros de historial.")

        print("\n¡Datos de demostración cargados correctamente! La base de datos está lista.")
    finally:
        db.close()


if __name__ == '__main__':
    seed()
