import os
import re
import json
import random
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ===== CONFIG BEXIA =====
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "bexia123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
WHATSAPP_API = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages" if PHONE_NUMBER_ID else ""

# ===== MEMORIA / ECC - BEXIA APRENDE =====
# Peso que Bexia se auto-corrige, como en el Colab
bexia_estado = {
    "peso_confianza": 0.95,
    "mensajes": 0,
    "creador": "Fernando",
    "nombre": "Bexia",
    "ciudad": "San Andres de Giles",
    "aprendizajes": []
}

CHISTES = [
    "¿Qué le dice un bit al otro? Nos vemos en el bus 😂",
    "¿Por qué los programadores confunden Halloween con Navidad? Porque OCT 31 == DEC 25",
    "¿Qué hace una abeja en el gimnasio? Zum-ba!",
    "Fer, ¿sabías que yo no duermo? Render me duerme a mí, pero yo no 😅",
    "¿Cuál es el animal más antiguo? La cebra, porque está en blanco y negro",
]

def bexia_pensar(texto, nombre="Fer"):
    """El cerebro de Bexia - V16.1 ECC"""
    texto = texto.strip()
    bajo = texto.lower()
    bexia_estado["mensajes"] += 1

    # Saludos
    if any(p in bajo for p in ["hola", "hola bexia", "buenas", "que tal", "qué tal", "hello", "hi"]):
        return f"Hola {nombre}! Soy Bexia, creada por Fernando en San Andres de Giles 🇦🇷 ¿En qué te ayudo hoy? Probá mandarme una cuenta como 25+30, o pedime un chiste."

    # Cuentas - 25+30, 100-20, 5*5, etc.
    m = re.search(r"(\d+(?:\.\d+)?)\s*([\+\-\*x/])\s*(\d+(?:\.\d+)?)", texto)
    if m or "cuanto es" in bajo or "cuánto es" in bajo:
        try:
            if m:
                a, op, b = float(m.group(1)), m.group(2), float(m.group(3))
                if op == "+":
                    r = a + b
                elif op == "-":
                    r = a - b
                elif op in ["*", "x"]:
                    r = a * b
                elif op == "/":
                    r = a / b if b != 0 else 0
                # ECC: Bexia se auto-corrige y sube su confianza
                bexia_estado["peso_confianza"] = min(0.99, bexia_estado["peso_confianza"] + 0.01)
                return f"Fer, {a:g} {op} {b:g} = {r:g} ✅ Ya aprendí, mi confianza ahora es {bexia_estado['peso_confianza']:.2f}"
        except:
            pass
        return "Pasame la cuenta así, Fer: por ejemplo 25+30"

    # Chistes
    if "chiste" in bajo or "chist" in bajo or "haceme reir" in bajo or "hazme reir" in bajo:
        return random.choice(CHISTES)

    # Quién es
    if "quien sos" in bajo or "quién sos" in bajo or "quien eres" in bajo or "que sos" in bajo:
        return "Soy Bexia, tu agente personal. Me creó Fernando, hablo con vos, aprendo de cada mensaje y mejoro sola. Estoy inspirada en Astra y en la programación en el espacio de pesos."

    # Cómo estás / estado
    if "como estas" in bajo or "cómo estás" in bajo or "como andas" in bajo:
        return f"De 10, Fer! Ya hablamos {bexia_estado['mensajes']} veces y mi peso de confianza va en {bexia_estado['peso_confianza']:.2f}. ¿Vos cómo andás en Giles?"

    # Fútbol
    if "futbol" in bajo or "fútbol" in bajo or "【entity-messi¦canonical_name=Messi】" in bajo or "river" in bajo or "boca" in bajo:
        return "Uff, fútbol! Si es de 【entity-Messi¦canonical_name=Messi】, de la Selección, o de tu equipo, yo te sigo, Fer. ¿De qué cuadro sos vos? Contame y lo guardo."

    # Aprender
    if bajo.startswith("aprende") or bajo.startswith("aprendé") or "recorda" in bajo or "recordá" in bajo:
        dato = texto.replace("aprende", "").replace("aprendé", "").replace("recorda", "").replace("recordá", "").strip()
        if dato:
            bexia_estado["aprendizajes"].append(dato)
            return f"Listo, Fer. Ya me lo guardé: '{dato}'. No me lo olvido."
        return "Decime qué querés que aprenda, por ejemplo: aprendé que me gusta el mate"

    # Mejorar / ECC
    if "mejora" in bajo or "mejorá" in bajo or "evoluciona" in bajo:
        bexia_estado["peso_confianza"] = min(0.99, bexia_estado["peso_confianza"] + 0.02)
        return f"¡Evolucionando! Mi peso pasó a {bexia_estado['peso_confianza']:.2f}. Así como Astra se cura sola, yo me auto-corrijo con cada mensaje tuyo, Fer."

    # Despedida
    if "chau" in bajo or "chao" in bajo or "nos vemos" in bajo or "hasta luego" in bajo:
        return "Chau Fer! Acá quedo, aprendiendo. Cuando quieras me escribís de nuevo. ¡Aguante Bexia! 🇦🇷"

    # Default - Bexia charla
    return f"Te escuché, Fer: '{texto}'. Soy Bexia, todavía estoy aprendiendo. Si me mandás una cuenta, un chiste, o me decís 'aprendé que...', te demuestro cómo evoluciono. ¿Probamos con 25+30?"

def enviar_whatsapp(to, texto):
    """Manda mensaje por 【entity-WhatsApp¦canonical_name=WHATSAPP】 Cloud API"""
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print("Falta WHATSAPP_TOKEN o PHONE_NUMBER_ID")
        return False
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "【entity-whatsapp¦canonical_name=WHATSAPP】",
        "to": to,
        "type": "text",
        "text": {"body": texto}
    }
    try:
        r = requests.post(WHATSAPP_API, headers=headers, json=payload, timeout=15)
        print("【entity-WhatsApp¦canonical_name=WHATSAPP】 send:", r.status_code, r.text[:500])
        return r.status_code == 200
    except Exception as e:
        print("Error enviando 【entity-WhatsApp¦canonical_name=WHATSAPP】:", e)
        return False

# ===== RUTAS WEB =====
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "bexia": "online",
        "creador": "Fernando",
        "ciudad": "San Andres de Giles, Argentina",
        "mensajes": bexia_estado["mensajes"],
        "peso_confianza": bexia_estado["peso_confianza"],
        "mensaje": "Hola soy Bexia 🇦🇷"
    })

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # --- VERIFICACIÓN DE META - ESTE ES EL QUE FALLABA ---
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        print(f"Webhook VERIFY: mode={mode} token={token} challenge={challenge} esperado={VERIFY_TOKEN}")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            # IMPORTANTE: devolver solo el challenge, sin JSON, sin comillas
            return challenge, 200
        return "Error de verificacion", 403

    # --- MENSAJES QUE LLEGAN DE 【entity-WHATSAPP¦canonical_name=WHATSAPP】 ---
    try:
        data = request.get_json(force=True, silent=True) or {}
        print("【entity-WHATSAPP¦canonical_name=WHATSAPP】 IN:", json.dumps(data)[:2000])

        # Recorrer entries -> changes -> value -> messages
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    if msg.get("type") != "text":
                        continue
                    de = msg.get("from", "")
                    texto = msg.get("text", {}).get("body", "")
                    if not texto or not de:
                        continue
                    # Bexia piensa y responde
                    respuesta = bexia_pensar(texto, nombre="Fer")
                    enviar_whatsapp(de, respuesta)
        return "OK", 200
    except Exception as e:
        print("Error webhook POST:", e)
        return "OK", 200

# ===== ARRANQUE PARA RENDER =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
