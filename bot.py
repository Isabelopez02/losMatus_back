"""
Bot de Telegram de soporte "Los Matus" (Matito).

Flujo Humanizado:
  1. El cliente inicia el bot (/start).
  2. Si es nuevo, el bot se presenta como "Matito" y pide el nombre.
  3. Luego pide el problema.
  4. La IA genera una pregunta de diagnóstico o sugerencia (manteniendo el historial corto).
  5. El cliente responde con más detalle.
  6. El bot pide enviar la ubicación real.
  7. Se crea el Cliente (si no existía) y el Ticket con todo el contexto.
"""
import sys
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters,
)

from app.config import settings
from app.services.ai_service import analizar_incidencia, generar_pregunta_diagnostico

API = settings.API_BASE_URL

# Estados de la conversación
NOMBRE, INDAGANDO, UBICACION = range(3)


# ----------------------------------------------------------------------------
# Helpers de API (backend FastAPI)
# ----------------------------------------------------------------------------
def buscar_cliente_por_telegram(telegram_id: str):
    try:
        r = requests.get(f"{API}/clientes/telegram/{telegram_id}", timeout=15)
        if r.status_code == 200:
            return r.json()
    except requests.RequestException as e:
        print(f"[bot] Error buscando cliente: {e}")
    return None


def crear_cliente(datos: dict):
    r = requests.post(f"{API}/clientes", json=datos, timeout=15)
    r.raise_for_status()
    return r.json()


def crear_ticket(datos: dict):
    r = requests.post(f"{API}/tickets", json=datos, timeout=15)
    r.raise_for_status()
    return r.json()


def crear_chat(datos: dict):
    try:
        requests.post(f"{API}/chats", json=datos, timeout=15)
    except requests.RequestException as e:
        print(f"[bot] Error guardando chat: {e}")


# ----------------------------------------------------------------------------
# Handlers de la conversación
# ----------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    context.user_data.clear()
    context.user_data["telegram_id"] = telegram_id
    context.user_data["historial_mensajes"] = []
    context.user_data["problema_completo_texto"] = ""

    cliente = buscar_cliente_por_telegram(telegram_id)
    if cliente:
        context.user_data["cliente"] = cliente
        context.user_data["nombre"] = cliente.get("nombre", "")
        await update.message.reply_text(
            f"Hola {cliente['nombre']}, ¿tuviste algún inconveniente hoy o en qué te puedo ayudar?",
            reply_markup=ReplyKeyboardRemove(),
        )
        return INDAGANDO

    await update.message.reply_text(
        "¡Hola! mucho gusto, te saluda tu asesor Matito 👋\n\n"
        "¿Con quién tengo el gusto? Me puede brindar su nombre por favor...",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NOMBRE


async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    partes = update.message.text.strip().split()
    nombre = partes[0]
    context.user_data["nombre"] = nombre
    context.user_data["apellido_paterno"] = partes[1] if len(partes) > 1 else ""
    context.user_data["apellido_materno"] = partes[2] if len(partes) > 2 else ""
    
    await update.message.reply_text(
        f"Perfecto {nombre}, cuéntame, ¿qué problema estás presentando o en qué te puedo ayudar?",
    )
    return INDAGANDO


async def indagar_problema(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.strip()
    
    # Acumular todo el texto para crear el ticket luego
    context.user_data["problema_completo_texto"] += f"Cliente: {mensaje}\n"
    
    # Agregamos al historial para la IA
    historial = context.user_data["historial_mensajes"]
    historial.append({"role": "user", "content": mensaje})
    
    await update.message.chat.send_action(action="typing")
    
    # Generar respuesta de la IA
    respuesta_ia = generar_pregunta_diagnostico(historial)
    historial.append({"role": "assistant", "content": respuesta_ia})
    context.user_data["problema_completo_texto"] += f"Matito: {respuesta_ia}\n"
    
    # Comprobar si la IA determinó que la indagación está COMPLETA
    if "[COMPLETO]" in respuesta_ia:
        respuesta_limpia = respuesta_ia.replace("[COMPLETO]", "").strip()
        
        boton = ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Compartir mi ubicación", request_location=True)]],
            resize_keyboard=True, one_time_keyboard=True,
        )
        
        # Enviar el mensaje final de la IA junto con la petición de ubicación
        mensaje_final = f"{respuesta_limpia}\n\n¿Me puedes enviar tu ubicación real por favor para poder enviar a un técnico? (O escribe /saltar)"
        await update.message.reply_text(mensaje_final, reply_markup=boton)
        return UBICACION
    else:
        # Seguir indagando
        await update.message.reply_text(respuesta_ia)
        return INDAGANDO


async def recibir_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    context.user_data["latitud"] = loc.latitude
    context.user_data["longitud"] = loc.longitude
    return await _procesar_y_crear_ticket(update, context)


async def saltar_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["latitud"] = None
    context.user_data["longitud"] = None
    return await _procesar_y_crear_ticket(update, context)


async def _procesar_y_crear_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    cliente = d.get("cliente")
    
    # 1. Crear o actualizar cliente si es nuevo
    if not cliente:
        payload = {
            "nombre": d.get("nombre"),
            "apellido_paterno": d.get("apellido_paterno") or None,
            "apellido_materno": d.get("apellido_materno") or None,
            "telegram_id": d.get("telegram_id"),
            "latitud": d.get("latitud"),
            "longitud": d.get("longitud"),
            "activo": True,
        }
        try:
            cliente = crear_cliente(payload)
            context.user_data["cliente"] = cliente
        except Exception as e:
            print(f"[bot] Error creando cliente: {e}")
            await update.message.reply_text(
                "⚠️ Hubo un problema registrando tus datos. Intenta con /start de nuevo.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END

    await update.message.reply_text("🤖 Registrando incidencia y asignando técnico...", reply_markup=ReplyKeyboardRemove())

    # Consolidar el problema de todo el historial de conversación
    problema_completo = d.get("problema_completo_texto", "Sin detalles.")

    # 2. Análisis definitivo con IA (para categorizar y sugerir al técnico en la BD)
    analisis = analizar_incidencia(problema_completo)

    # 3. Crear el ticket (RECIÉN AHORA SE CREA EL TICKET)
    ticket_payload = {
        "codigo": analisis["codigo"],
        "descripcion": analisis["resumen"],  # Se usa el resumen de la IA en vez de todo el chat
        "categoria": analisis["categoria"],
        "severidad": analisis["severidad"],
        "sugerencia_ia": analisis.get("sugerencia"),
        "estado_incidencia": "Abierto",
        "cumple_sla": True,
        "id_usuario": cliente["id_usuario"],
    }
    try:
        ticket = crear_ticket(ticket_payload)
    except Exception as e:
        print(f"[bot] Error creando ticket: {e}")
        await update.message.reply_text("⚠️ No pude registrar el ticket. Verifica que el sistema esté activo.")
        return ConversationHandler.END

    # 4. Guardar los mensajes del chat como evidencia en la base de datos
    for msg in d.get("historial_mensajes", []):
        crear_chat({
            "mensaje": msg["content"],
            "tipo_mensaje": "texto" if msg["role"] == "user" else "bot",
            "id_incidencia": ticket["id_incidencia"],
            "id_usuario": cliente["id_usuario"],
        })

    # 5. Responder al cliente
    icono_ia = "🧠 (Asistido por IA)" if analisis.get("con_ia") else "⚙️"
    await update.message.reply_text(
        f"¡Listo {d.get('nombre')}! Tu problema ha sido registrado y un técnico ha sido asignado.\n\n"
        f"📋 *Ticket:* `{ticket['codigo']}`\n"
        f"⚠️ *Severidad:* {analisis['severidad']}\n\n"
        f"Cualquier novedad te contactaremos por aquí. {icono_ia}\n"
        "Puedes reportar otra incidencia con /start.",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada. Escribe /start cuando quieras.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


bot_app = None

async def start_bot():
    global bot_app
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if not settings.TELEGRAM_BOT_TOKEN:
        print("ERROR: Falta TELEGRAM_BOT_TOKEN en el .env.")
        return

    bot_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)],
            INDAGANDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, indagar_problema)],
            UBICACION: [
                MessageHandler(filters.LOCATION, recibir_ubicacion),
                CommandHandler("saltar", saltar_ubicacion),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    bot_app.add_handler(conv)
    
    # Manejador global para cuando el cliente escribe pero NO está en proceso de crear ticket
    # (por ejemplo, cuando chatea con el técnico a través del dashboard)
    async def mensaje_libre(update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = str(update.effective_user.id)
        mensaje = update.message.text.strip()
        
        # Buscar cliente
        cliente = buscar_cliente_por_telegram(telegram_id)
        if not cliente:
            # Si no existe, sugerimos iniciar el bot
            await update.message.reply_text("Hola, por favor usa /start para registrar tu problema.")
            return

        # Obtener los tickets del cliente para encontrar el último activo
        try:
            r = requests.get(f"{API}/clientes/{cliente['id_usuario']}/tickets", timeout=10)
            if r.status_code == 200:
                tickets = r.json()
                # Buscar el primer ticket Abierto o En Proceso
                ticket_activo = next((t for t in sorted(tickets, key=lambda x: x['id_incidencia'], reverse=True) 
                                     if t['estado_incidencia'] in ['Abierto', 'En Proceso']), None)
                
                if ticket_activo:
                    # Guardamos el mensaje en el historial del ticket para que el técnico lo vea
                    crear_chat({
                        "mensaje": mensaje,
                        "tipo_mensaje": "texto",
                        "id_incidencia": ticket_activo['id_incidencia'],
                        "id_usuario": cliente['id_usuario']
                    })
                    # Si el técnico aún no lo ha tomado (Abierto), le damos un aviso automático.
                    # Si ya está "En Proceso", el bot se silencia totalmente porque el técnico está hablando.
                    if ticket_activo['estado_incidencia'] == 'Abierto':
                        await update.message.reply_text("Tu incidencia ya está registrada y estamos buscando un técnico disponible para ti. ¡Pronto te escribirán por aquí!")
                else:
                    await update.message.reply_text("No tienes incidencias activas en este momento. Si tienes un nuevo problema, usa /start.")
        except Exception as e:
            print(f"[bot] Error guardando mensaje libre: {e}")

    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_libre))

    print("🤖 Bot de Telegram 'Matito' iniciando en segundo plano...")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    print("🤖 Bot de Telegram 'Matito' está escuchando mensajes.")

async def stop_bot():
    global bot_app
    if bot_app:
        print("🛑 Deteniendo Bot de Telegram 'Matito'...")
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
        print("🛑 Bot detenido.")
