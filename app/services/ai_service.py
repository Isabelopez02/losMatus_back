"""
Servicio de IA para analizar y clasificar incidencias de soporte.

Usa Groq (API gratuita, compatible con OpenAI) si hay GROQ_API_KEY en el .env.
Si no hay clave o la llamada falla, cae a un clasificador por palabras clave,
de modo que el sistema SIEMPRE funciona.
"""
import json
import random
import requests
from app.config import settings

CATEGORIAS = ["Hardware", "Software", "Red", "Configuración", "Otro"]
SEVERIDADES = ["Baja", "Media", "Alta", "Crítica"]

SYSTEM_PROMPT = (
    "Eres el asistente de soporte técnico de 'Los Matus', una empresa de seguridad "
    "electrónica (cámaras CCTV, DVR, lectores biométricos, alarmas). "
    "Analiza el mensaje del cliente y responde SOLO con un JSON válido, sin texto extra, "
    "con esta forma exacta:\n"
    '{"categoria": "Hardware|Software|Red|Configuración|Otro", '
    '"severidad": "Baja|Media|Alta|Crítica", '
    '"resumen": "descripción técnica breve del problema en una frase", '
    '"respuesta": "mensaje cordial y claro para el cliente confirmando que se registró su incidencia", '
    '"sugerencia": "recomendación técnica concreta para el TÉCNICO que atenderá: qué revisar, '
    'qué repuestos/herramientas llevar y posible causa. Máximo 2 frases."}'
)

# Sugerencias de respaldo por categoría (cuando no hay IA externa)
SUGERENCIAS_REGLAS = {
    "Hardware": "Asistir al local con repuestos (conectores RJ45, herramientas de crimpado, inyector PoE) "
                "y multímetro. Revisar alimentación, cableado y estado físico del equipo.",
    "Software": "Verificar versión de firmware y configuración. Respaldar la configuración actual antes de "
                "actualizar o reinstalar.",
    "Red": "Comprobar conectividad, cableado de red y configuración IP. Llevar tester de red y verificar el switch/PoE.",
    "Configuración": "Revisar los parámetros de configuración del equipo y las credenciales de acceso. "
                     "Confirmar horarios/reglas programadas.",
    "Otro": "Contactar al cliente para obtener más detalles antes de asignar al técnico y definir el repuesto necesario.",
}


def _generar_codigo() -> str:
    return f"TCK-{random.randint(1000, 9999)}"


def _clasificar_por_reglas(mensaje: str) -> dict:
    """Clasificador de respaldo sin IA externa."""
    texto = (mensaje or "").lower()

    # Categoría
    if any(k in texto for k in ["no enciende", "pantalla", "cable", "quemad", "roto", "físic", "camara", "cámara", "dvr", "disco", "fuente", "hardware"]):
        categoria = "Hardware"
    elif any(k in texto for k in ["software", "app", "aplicación", "firmware", "actualiz", "clave", "contraseña", "usuario", "login", "sistema"]):
        categoria = "Software"
    elif any(k in texto for k in ["internet", "red", "wifi", "conexión", "conexion", "ip", "offline", "sin señal", "no conecta"]):
        categoria = "Red"
    elif any(k in texto for k in ["config", "ajuste", "instalar", "instalación", "programar", "horario"]):
        categoria = "Configuración"
    else:
        categoria = "Otro"

    # Severidad
    if any(k in texto for k in ["urgente", "crític", "critic", "no funciona nada", "todo el sistema", "seguridad comprometida", "robo", "emergencia"]):
        severidad = "Crítica"
    elif any(k in texto for k in ["no enciende", "no graba", "no funciona", "caíd", "caid", "sin señal", "apagad"]):
        severidad = "Alta"
    elif any(k in texto for k in ["intermitente", "a veces", "lento", "demora"]):
        severidad = "Media"
    else:
        severidad = "Media"

    return {
        "categoria": categoria,
        "severidad": severidad,
        "resumen": (mensaje or "").strip()[:250] or "Incidencia reportada por el cliente",
        "respuesta": "He registrado tu incidencia y un técnico la revisará a la brevedad.",
        "sugerencia": SUGERENCIAS_REGLAS.get(categoria, SUGERENCIAS_REGLAS["Otro"]),
    }


def _clasificar_con_groq(mensaje: str) -> dict:
    """Llama a Groq (compatible OpenAI). Lanza excepción si falla."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": mensaje},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=25)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    data = json.loads(content)

    # Normalización / validación
    categoria = data.get("categoria", "Otro")
    severidad = data.get("severidad", "Media")
    categoria = categoria if categoria in CATEGORIAS else "Otro"
    return {
        "categoria": categoria,
        "severidad": severidad if severidad in SEVERIDADES else "Media",
        "resumen": (data.get("resumen") or mensaje).strip()[:250],
        "respuesta": data.get("respuesta") or "He registrado tu incidencia. Un técnico la atenderá pronto.",
        "sugerencia": (data.get("sugerencia") or SUGERENCIAS_REGLAS.get(categoria, SUGERENCIAS_REGLAS["Otro"])).strip()[:500],
    }


def analizar_incidencia(mensaje: str) -> dict:
    """
    Devuelve un dict con: categoria, severidad, resumen, respuesta, codigo, con_ia (bool).
    """
    resultado = None
    con_ia = False

    if settings.GROQ_API_KEY:
        try:
            resultado = _clasificar_con_groq(mensaje)
            con_ia = True
        except Exception as e:  # noqa: BLE001
            print(f"[ai_service] Falló Groq, usando reglas. Detalle: {e}")

    if resultado is None:
        resultado = _clasificar_por_reglas(mensaje)

    resultado["codigo"] = _generar_codigo()
    resultado["con_ia"] = con_ia
    return resultado
