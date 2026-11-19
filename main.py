import json
import logging
import os
import re
import sqlite3
from datetime import datetime, timezone
from flask import Flask, jsonify, request
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bexia")

app = Flask(__name__)

# ===== CONFIG =====
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "bexia123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
WHATSAPP_API = (
    f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    if PHONE_NUMBER_ID
    else ""
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
SQLITE_PATH = os.environ.get("SQLITE_PATH", "bexia.db")

CREADOR = "Fernando Brito"
CIUDAD = "San Andrés de Giles"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(SQLITE_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    db_dir = os.path.dirname(os.path.abspath(SQLITE_PATH))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                numero TEXT PRIMARY KEY,
                nombre TEXT NOT NULL DEFAULT 'Fer',
                equipo TEXT NOT NULL DEFAULT '',
                veces INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS gustos_usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                gusto TEXT NOT NULL,
                UNIQUE(numero, gusto),
                FOREIGN KEY(numero) REFERENCES usuarios(numero) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS aprendizajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_origen TEXT NOT NULL,
                dato TEXT NOT NULL,
                creado_en TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS historial_chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'model')),
                texto TEXT NOT NULL,
                creado_en TEXT NOT NULL,
                FOREIGN KEY(numero) REFERENCES usuarios(numero) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS estado_global (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            );

            INSERT OR IGNORE INTO estado_global (clave, valor) VALUES ('mensajes_totales', '0');
            INSERT OR IGNORE INTO estado_global (clave, valor) VALUES ('peso_confianza', '0.95');
            """
        )


def obtener_estado_global() -> dict:
    with get_conn() as conn:
        rows = conn.execute("SELECT clave, valor FROM estado_global").fetchall()
    mapa = {r["clave"]: r["valor"] for r in rows}
    return {
        "mensajes_totales": int(mapa.get("mensajes_totales", "0")),
        "peso_confianza": float(mapa.get("peso_confianza", "0.95")),
        "creador": CREADOR,
        "ciudad": CIUDAD,
    }


def incrementar_mensajes_y_confianza(delta_confianza: float = 0.0) -> dict:
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        actual_msg = conn.execute(
            "SELECT valor FROM estado_global WHERE clave = 'mensajes_totales'"
        ).fetchone()
        actual_conf = conn.execute(
            "SELECT valor FROM estado_global WHERE clave = 'peso_confianza'"
        ).fetchone()

        nuevo_msg = int(actual_msg["valor"]) + 1 if actual_msg else 1
        nueva_conf = float(actual_conf["valor"]) if actual_conf else 0.95
        if delta_confianza:
            nueva_conf = min(0.99, round(nueva_conf + delta_confianza, 2))

        conn.execute(
            "UPDATE estado_global SET valor = ? WHERE clave = 'mensajes_totales'",
            (str(nuevo_msg),),
        )
        conn.execute(
            "UPDATE estado_global SET valor = ? WHERE clave = 'peso_confianza'",
            (str(nueva_conf),),
        )
        conn.commit()

    estado = obtener_estado_global()
    estado["actualizado_en"] = now_iso
    return estado


def asegurar_usuario(numero: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO usuarios (numero, nombre, equipo, veces) VALUES (?, 'Fer', '', 0)",
            (numero,),
        )
        conn.commit()


def incrementar_veces_usuario(numero: str) -> int:
    asegurar_usuario(numero)
    with get_conn() as conn:
        conn.execute(
            "UPDATE usuarios SET veces = veces + 1 WHERE numero = ?",
            (numero,),
        )
        row = conn.execute(
            "SELECT veces FROM usuarios WHERE numero = ?",
            (numero,),
        ).fetchone()
        conn.commit()
    return int(row["veces"]) if row else 1


def actualizar_nombre_usuario(numero: str, nombre: str) -> None:
    asegurar_usuario(numero)
    with get_conn() as conn:
        conn.execute(
            "UPDATE usuarios SET nombre = ? WHERE numero = ?",
            (nombre, numero),
        )
        conn.commit()


def actualizar_equipo_usuario(numero: str, equipo: str) -> None:
    asegurar_usuario(numero)
    with get_conn() as conn:
        conn.execute(
            "UPDATE usuarios SET equipo = ? WHERE numero = ?",
            (equipo, numero),
        )
        conn.commit()


def agregar_gusto_usuario(numero: str, gusto: str) -> None:
    gusto_limpio = gusto.strip()
    if not gusto_limpio:
        return
    asegurar_usuario(numero)
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO gustos_usuario (numero, gusto) VALUES (?, ?)",
            (numero, gusto_limpio),
        )
        conn.commit()


def agregar_aprendizaje(numero: str, dato: str) -> None:
    dato_limpio = dato.strip()
    if not dato_limpio:
        return
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO aprendizajes (numero_origen, dato, creado_en) VALUES (?, ?, ?)",
            (numero, dato_limpio, now_iso),
        )
        conn.commit()


def obtener_aprendizajes_recientes(limite: int = 10) -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT dato FROM aprendizajes ORDER BY id DESC LIMIT ?",
            (limite,),
        ).fetchall()
    return [r["dato"] for r in reversed(rows)]


def agregar_mensaje_historial(numero: str, role: str, texto: str) -> None:
    asegurar_usuario(numero)
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO historial_chat (numero, role, texto, creado_en) VALUES (?, ?, ?, ?)",
            (numero, role, texto, now_iso),
        )
        conn.commit()


def limpiar_historial_usuario(numero: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM historial_chat WHERE numero = ?",
            (numero,),
        )
        conn.commit()


def obtener_historial_reciente(numero: str, limite: int = 8) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT role, texto
            FROM historial_chat
            WHERE numero = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (numero, limite),
        ).fetchall()
    return [{"role": r["role"], "text": r["texto"]} for r in reversed(rows)]


def cargar_contexto_usuario(numero: str) -> dict:
    asegurar_usuario(numero)
    with get_conn() as conn:
        u = conn.execute(
            "SELECT numero, nombre, equipo, veces FROM usuarios WHERE numero = ?",
            (numero,),
        ).fetchone()
        gustos_rows = conn.execute(
            "SELECT gusto FROM gustos_usuario WHERE numero = ? ORDER BY id ASC",
            (numero,),
        ).fetchall()

    return {
        "numero": numero,
        "nombre": u["nombre"] if u else "Fer",
        "equipo": u["equipo"] if u else "",
        "veces": int(u["veces"]) if u else 0,
        "gustos": [r["gusto"] for r in gustos_rows],
        "historial": obtener_historial_reciente(numero, limite=8),
    }


def normalizar(t: str) -> str:
    t = t.lower().strip()
    reemplazos = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u",
        "¿": "", "?": "", "¡": "", "!": "", ".": "", ",": "",
    }
    for k, v in reemplazos.items():
        t = t.replace(k, v)
    return re.sub(r"\s+", " ", t).strip()


def construir_prompt_sistema(user: dict, estado: dict, aprendizajes: list[str]) -> str:
    nombre = user.get("nombre", "Fer")
    equipo = user.get("equipo") or "no especificado"
    gustos = ", ".join(user.get("gustos", [])[-6:]) or "ninguno anotado"
    aprendizajes_txt = ", ".join(aprendizajes[-10:]) or "ninguno aún"

    return (
        f"Sos Bexia, una asistente personal estilo mini-Gemini creada por "
        f"{estado.get('creador', CREADOR)} en "
        f"{estado.get('ciudad', CIUDAD)}, Argentina. "
        f"Hablás en español rioplatense natural, claro, amable y directo. "
        f"Ayudás a responder preguntas, explicar temas, resumir, dar ideas, resolver "
        f"problemas o charlar. Si algo es ambiguo o no lo sabés con certeza, decilo "
        f"con claridad en vez de inventar. "
        f"Como respondés por WhatsApp, usá párrafos cortos y viñetas simples cuando "
        f"ayude a leer mejor, sin markdown pesado. "
        f"Contexto del usuario: nombre={nombre}, equipo={equipo}, "
        f"gustos_y_notas=[{gustos}]. "
        f"Aprendizajes guardados: [{aprendizajes_txt}]."
    )


def preguntar_gemini(user: dict, estado: dict, aprendizajes: list[str]) -> str:
    nombre = user.get("nombre", "Fer")

    if not GEMINI_API_KEY:
        return (
            f"Todavía no tengo configurada la clave GEMINI_API_KEY, {nombre}. "
            f"Cuando la cargues en el entorno, voy a poder responderte como mini-Gemini."
        )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
    )
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json",
    }

    contents = [
        {"role": turno["role"], "parts": [{"text": turno["text"]}]}
        for turno in user.get("historial", [])[-8:]
    ]

    payload = {
        "systemInstruction": {
            "parts": [{"text": construir_prompt_sistema(user, estado, aprendizajes)}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 450,
        },
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        candidatos = data.get("candidates", [])
        if candidatos:
            partes = candidatos[0].get("content", {}).get("parts", [])
            texto_generado = "".join(p.get("text", "") for p in partes).strip()
            if texto_generado:
                return texto_generado

        return f"No pude armar una respuesta esta vez, {nombre}. ¿Probás preguntarlo de otra forma?"
    except requests.RequestException:
        return (
            f"Tuve un problema al conectarme para pensar la respuesta, {nombre}. "
            f"Intentemos de nuevo en un momento."
        )


def bexia_pensar(texto_original: str, numero: str = "anonimo") -> str:
    texto = texto_original.strip()
    bajo = normalizar(texto)

    incrementar_veces_usuario(numero)
    estado = incrementar_mensajes_y_confianza(0.0)
    user = cargar_contexto_usuario(numero)
    nombre = user["nombre"]

    # --- Reiniciar conversación ---
    if bajo in ["nueva charla", "reset", "borrar historial", "limpiar chat"]:
        limpiar_historial_usuario(numero)
        return (
            f"Listo, {nombre}. Borré el historial de esta charla, "
            f"pero sigo conservando tus datos guardados."
        )

    agregar_mensaje_historial(numero, "user", texto)
    user["historial"] = obtener_historial_reciente(numero, limite=8)

    # --- Aprender nombre ---
    m_nombre = re.search(
        r"^(?:hola,?\s*)?(?:me llamo|mi nombre es|soy)\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ]+(?:\s+[a-zA-ZáéíóúÁÉÍÓÚñÑ]+)?)$",
        texto,
        re.I,
    )
    if m_nombre:
        candidato = m_nombre.group(1).strip()
        if candidato.lower() not in {"hincha", "de", "bexia"} and len(candidato) <= 25:
            nuevo_nombre = candidato.title()
            actualizar_nombre_usuario(numero, nuevo_nombre)
            respuesta = f"¡Genial, {nuevo_nombre}! Ya guardé tu nombre en mi base. ¿En qué te ayudo hoy?"
            agregar_mensaje_historial(numero, "model", respuesta)
            return respuesta

    # --- Aprender equipo ---
    m_equipo = re.search(
        r"(?:soy hincha de|soy de|mi equipo es)\s+(?:el\s+|la\s+)?([a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]{2,30})",
        texto,
        re.I,
    )
    if m_equipo and not re.search(
        r"\b(san andres de giles|giles|argentina)\b",
        normalizar(m_equipo.group(1)),
    ):
        equipo = m_equipo.group(1).strip().title()
        actualizar_equipo_usuario(numero, equipo)
        agregar_gusto_usuario(numero, f"hincha de {equipo}")
        respuesta = f"¡Anotado, {nombre}! Guardé que sos hincha de {equipo}."
        agregar_mensaje_historial(numero, "model", respuesta)
        return respuesta

    # --- Aprender dato explícito ---
    m_aprende = re.match(
        r"^(?:aprende|aprendé|recorda|recordá)(?:\s+que)?\s+(.+)$",
        texto,
        re.I,
    )
    if m_aprende:
        dato = m_aprende.group(1).strip()
        agregar_aprendizaje(numero, dato)
        agregar_gusto_usuario(numero, dato)
        estado = incrementar_mensajes_y_confianza(0.01)
        respuesta = (
            f"Listo, {nombre}. Guardé esto en SQLite: '{dato}' "
            f"(confianza: {estado['peso_confianza']:.2f})."
        )
        agregar_mensaje_historial(numero, "model", respuesta)
        return respuesta

    # --- Ver memoria guardada ---
    if any(
        frase in bajo
        for frase in ["que sabes de mi", "que sabes sobre mi", "te acordas de mi"]
    ):
        partes = [f"tu nombre es {nombre}", f"ya hablamos {user['veces']} veces"]
        if user["equipo"]:
            partes.append(f"sos hincha de {user['equipo']}")
        if user["gustos"]:
            partes.append(f"gustos/notas: {', '.join(user['gustos'][-4:])}")
        respuesta = f"Esto tengo guardado de vos, {nombre}: " + " | ".join(partes) + "."
        agregar_mensaje_historial(numero, "model", respuesta)
        return respuesta

    # --- Ayuda rápida ---
    if bajo in ["ayuda", "help", "que podes hacer", "que puedes hacer"]:
        respuesta = (
            f"Soy Bexia (versión mini-Gemini con memoria en SQLite), {nombre}. Podés:\n"
            f"• Preguntarme o pedirme que te explique cualquier tema\n"
            f"• Decirme 'soy de...' o 'aprendé que...' para guardar datos\n"
            f"• Preguntarme '¿qué sabés de mí?'\n"
            f"• Escribir 'nueva charla' para borrar el historial del chat"
        )
        agregar_mensaje_historial(numero, "model", respuesta)
        return respuesta

    # --- Todo lo demás va directo a Gemini ---
    aprendizajes = obtener_aprendizajes_recientes(limite=10)
    respuesta = preguntar_gemini(user, estado, aprendizajes)
    agregar_mensaje_historial(numero, "model", respuesta)
    return respuesta


def enviar_whatsapp(to: str, texto: str) -> bool:
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        logger.warning("Falta WHATSAPP_TOKEN o PHONE_NUMBER_ID")
        return False

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": texto},
    }
    try:
        r = requests.post(WHATSAPP_API, headers=headers, json=payload, timeout=15)
        logger.info("WhatsApp send status=%s body=%s", r.status_code, r.text[:500])
        return 200 <= r.status_code < 300
    except requests.RequestException as e:
        logger.error("Error enviando WhatsApp: %s", e)
        return False


init_db()


@app.route("/", methods=["GET"])
def home():
    estado = obtener_estado_global()
    return jsonify({
        "bexia": "online",
        "storage": "sqlite",
        "sqlite_path": SQLITE_PATH,
        "creador": estado["creador"],
        "ciudad": estado["ciudad"],
        "mensajes": estado["mensajes_totales"],
        "peso_confianza": estado["peso_confianza"],
        "mensaje": "¡Hola! Soy Bexia 🇦🇷",
    })


@app.route("/health", methods=["GET"])
def health():
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1").fetchone()
        return "OK", 200
    except sqlite3.Error as e:
        logger.error("Healthcheck SQLite error: %s", e)
        return "DB ERROR", 500


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        logger.info("Webhook VERIFY mode=%s token_ok=%s", mode, token == VERIFY_TOKEN)
        if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
            return challenge, 200
        return "Error de verificacion", 403

    try:
        data = request.get_json(force=True, silent=True) or {}
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    if msg.get("type") != "text":
                        continue
                    de = msg.get("from", "")
                    texto = msg.get("text", {}).get("body", "")
                    if not texto or not de:
                        continue
                    respuesta = bexia_pensar(texto, numero=de)
                    enviar_whatsapp(de, respuesta)
        return "OK", 200
    except Exception as e:
        logger.exception("Error webhook POST: %s", e)
        return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
