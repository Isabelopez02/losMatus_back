"""
Bot de Telegram de soporte "Los Matus".

Flujo:
  1. El cliente inicia el bot (/start).
  2. Si es nuevo, el bot recopila sus datos (nombre, email, teléfono, dirección)
     y le pide COMPARTIR SU UBICACIÓN (para Google Maps).
  3. El cliente describe su problema en lenguaje natural.
  4. La IA (Groq) clasifica la incidencia (categoría + severidad + resumen).
  5. El bot crea el Cliente (si no existía), el Ticket y el log de chat en el backend.
  6. Responde con el número de ticket y el análisis.

Requisitos:
  - Definir TELEGRAM_BOT_TOKEN en el .env (token de @BotFather).
  - El backend FastAPI debe estar corriendo (python run.py).
  - Opcional: GROQ_API_KEY en el .env para el análisis con IA real.

Ejecutar:  python bot.py
"""
import sys
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters,
)

from app.config import settings
from app.services.ai_service import analizar_incidencia

API = settings.API_BASE_URL

# Estados de la conversación
NOMBRE, EMAIL, TELEFONO, DIRECCION, UBICACION, PROBLEMA = range(6)


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


def actualizar_cliente(id_usuario: int, datos: dict):
    r = requests.put(f"{API}/clientes/{id_usuario}", json=datos, timeout=15)
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

    cliente = buscar_cliente_por_telegram(telegram_id)
    if cliente:
        context.user_data["cliente"] = cliente
        await update.message.reply_text(
            f"¡Hola de nuevo, {cliente['nombre']}! 👋\n"
            "Soy el asistente de soporte de *Los Matus*.\n\n"
            "Cuéntame, ¿qué problema estás presentando?",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        return PROBLEMA

    await update.message.reply_text(
        "¡Hola! 👋 Soy el asistente de soporte de *Los Matus* (seguridad electrónica).\n\n"
        "Voy a registrar tu incidencia. Primero, unos datos rápidos.\n\n"
        "¿Cuál es tu *nombre completo*?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NOMBRE


async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    partes = update.message.text.strip().split()
    context.user_data["nombre"] = partes[0]
    context.user_data["apellido_paterno"] = partes[1] if len(partes) > 1 else ""
    context.user_data["apellido_materno"] = partes[2] if len(partes) > 2 else ""
    await update.message.reply_text("📧 ¿Cuál es tu *correo electrónico*? (o escribe /saltar)", parse_mode="Markdown")
    return EMAIL


async def recibir_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text.strip()
    await update.message.reply_text("📱 ¿Cuál es tu *número de teléfono*?", parse_mode="Markdown")
    return TELEFONO


async def saltar_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = None
    await update.message.reply_text("📱 ¿Cuál es tu *número de teléfono*?", parse_mode="Markdown")
    return TELEFONO


async def recibir_telefono(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["telefono"] = update.message.text.strip()
    await update.message.reply_text("🏠 ¿Cuál es tu *dirección*?", parse_mode="Markdown")
    return DIRECCION


async def recibir_direccion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["direccion"] = update.message.text.strip()
    boton = ReplyKeyboardMarkup(
        [[KeyboardButton("📍 Compartir mi ubicación", request_location=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )
    await update.message.reply_text(
        "📍 Por favor, *comparte tu ubicación* para que el técnico pueda llegar.\n"
        "(o escribe /saltar si prefieres no hacerlo)",
        parse_mode="Markdown", reply_markup=boton,
    )
    return UBICACION


async def recibir_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    context.user_data["latitud"] = loc.latitude
    context.user_data["longitud"] = loc.longitude
    return await _crear_cliente_y_pedir_problema(update, context)


async def saltar_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["latitud"] = None
    context.user_data["longitud"] = None
    return await _crear_cliente_y_pedir_problema(update, context)


async def _crear_cliente_y_pedir_problema(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    payload = {
        "nombre": d.get("nombre"),
        "apellido_paterno": d.get("apellido_paterno") or None,
        "apellido_materno": d.get("apellido_materno") or None,
        "email": d.get("email") or None,
        "telefono": d.get("telefono") or None,
        "direccion": d.get("direccion") or None,
        "telegram_id": d.get("telegram_id"),
        "latitud": d.get("latitud"),
        "longitud": d.get("longitud"),
        "activo": True,
    }
    try:
        cliente = crear_cliente(payload)
        context.user_data["cliente"] = cliente
    except Exception as e:  # noqa: BLE001
        print(f"[bot] Error creando cliente: {e}")
        await update.message.reply_text(
            "⚠️ Hubo un problema registrando tus datos. ¿El backend está corriendo? Intenta con /start de nuevo.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        f"✅ ¡Datos registrados, {cliente['nombre']}!\n\n"
        "Ahora cuéntame: ¿qué problema estás presentando? Descríbelo con tus palabras.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PROBLEMA


async def recibir_problema(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.strip()
    cliente = context.user_data.get("cliente")

    if not cliente:
        await update.message.reply_text("Empecemos de nuevo con /start, por favor.")
        return ConversationHandler.END

    await update.message.reply_text("🤖 Analizando tu incidencia con IA...")

    # 1. Análisis con IA
    analisis = analizar_incidencia(mensaje)

    # 2. Crear el ticket
    ticket_payload = {
        "codigo": analisis["codigo"],
        "descripcion": mensaje,
        "categoria": analisis["categoria"],
        "severidad": analisis["severidad"],
        "sugerencia_ia": analisis.get("sugerencia"),
        "estado_incidencia": "Abierto",
        "cumple_sla": True,
        "id_usuario": cliente["id_usuario"],
    }
    try:
        ticket = crear_ticket(ticket_payload)
    except Exception as e:  # noqa: BLE001
        print(f"[bot] Error creando ticket: {e}")
        await update.message.reply_text("⚠️ No pude registrar el ticket. Verifica que el backend esté activo.")
        return ConversationHandler.END

    # 3. Guardar el mensaje del chat
    crear_chat({
        "mensaje": mensaje,
        "tipo_mensaje": "texto",
        "id_incidencia": ticket["id_incidencia"],
        "id_usuario": cliente["id_usuario"],
    })

    # 4. Responder al cliente
    icono_ia = "🧠 (IA)" if analisis.get("con_ia") else "⚙️ (reglas)"
    await update.message.reply_text(
        f"{analisis.get('respuesta', 'He registrado tu incidencia.')}\n\n"
        f"📋 *Ticket:* `{ticket['codigo']}`\n"
        f"📂 *Categoría:* {analisis['categoria']}\n"
        f"⚠️ *Severidad:* {analisis['severidad']}\n"
        f"🔎 *Resumen:* {analisis['resumen']}\n"
        f"_Análisis {icono_ia}_\n\n"
        "Un técnico ha sido notificado. Puedes reportar otra incidencia con /start.",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada. Escribe /start cuando quieras.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    # La consola de Windows usa cp1252 y no puede imprimir emojis; forzamos UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    if not settings.TELEGRAM_BOT_TOKEN:
        print("ERROR: Falta TELEGRAM_BOT_TOKEN en el .env. Crea el bot con @BotFather y pega el token.")
        return

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)],
            EMAIL: [
                CommandHandler("saltar", saltar_email),
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_email),
            ],
            TELEFONO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_telefono)],
            DIRECCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_direccion)],
            UBICACION: [
                MessageHandler(filters.LOCATION, recibir_ubicacion),
                CommandHandler("saltar", saltar_ubicacion),
            ],
            PROBLEMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_problema)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv)
    print("🤖 Bot de Telegram 'Los Matus' iniciado. Esperando mensajes...")
    app.run_polling()


if __name__ == "__main__":
    main()
