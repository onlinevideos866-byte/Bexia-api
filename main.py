import os
import re
import json
import random
import requests
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# ===== CONFIG =====
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "bexia123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
WHATSAPP_API = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages" if PHONE_NUMBER_ID else ""

# ===== CEREBRO DE BEXIA - INTELIGENCIA TIPO 【entity-META¦canonical_name=Meta】 =====
# Memoria por usuario (por número de WhatsApp)
memoria_usuarios = {}
# Memoria global de Bexia
bexia_estado = {
    "peso_confianza": 0.95,
    "mensajes_totales": 0,
    "creador": "Fernando",
    "ciudad": "San Andres de Giles",
    "aprendizajes": []
}

CHISTES = [
    "¿Qué le dice un bit al otro? Nos vemos en el bus 😂",
    "¿Por qué los programadores confunden Halloween con Navidad? Porque OCT 31 == DEC 25",
    "¿Qué hace una abeja en el gimnasio? Zum-ba!",
    "Fer, ¿sabías que yo no duermo? Render me duerme a mí, pero yo no 😅",
    "¿Cuál es el animal más antiguo? La cebra, porque está en blanco y negro",
    "¿Qué le dice un 0 a un 8? Lindo cinturón!",
]

def normalizar(t):
    t = t.lower().strip()
    t = t.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
    t = t.replace("¿","").replace("?","").replace("!","").replace(".","").replace(",","")
    return t

def get_usuario(numero):
    if numero not in memoria_usuarios:
        memoria_usuarios[numero] = {
            "nombre": "Fer",
            "historial": [],  # últimos 10 mensajes
            "gustos": [],
            "equipo": "",
            "ultimo_tema": "",
            "veces": 0
        }
    return memoria_usuarios[numero]

def bexia_pensar(texto_original, numero="anonimo"):
    texto = texto_original.strip()
    bajo = normalizar(texto)
    user = get_usuario(numero)
    user["veces"] += 1
    user["historial"].append(texto)
    user["historial"] = user["historial"][-10:]
    bexia_estado["mensajes_totales"] += 1

    # --- APRENDER NOMBRE: "me llamo..." / "soy..." ---
    m_nombre = re.search(r"(me llamo|soy|mi nombre es)\s+([a-zA-Záéíóú ]+)", texto, re.I)
    if m_nombre and "bexia" not in bajo:
        nombre = m_nombre.group(2).strip().title()
        if len(nombre) < 25:
            user["nombre"] = nombre
            return f"Un gusto, {nombre}! Ya me lo guardo. Yo soy Bexia, creada por Fernando. ¿En qué te ayudo, {nombre}?"
    nombre = user["nombre"]

    # --- APRENDER EQUIPO / GUSTOS ---
    if "soy de" in bajo or "soy hincha de" in bajo or "mi equipo es" in bajo:
        equipo = texto.split("de")[-1].strip()
        user["equipo"] = equipo
        user["gustos"].append(f"hincha de {equipo}")
        return f"¡Aguante {equipo}! Ya me lo anoto, {nombre}. Sos hincha de {equipo}. ¿Querés que te cuente algo de fútbol o seguimos con otra cosa?"

    if "me gusta" in bajo:
        gusto = texto.lower().split("me gusta")[-1].strip()
        if gusto:
            user["gustos"].append(gusto)
            return f"Listo, {nombre}. Ya sé que te gusta {gusto}. Me lo guardo para la próxima charla."

    # --- APRENDER DATO: "aprende que..." / "recorda que..." ---
    if bajo.startswith("aprende") or bajo.startswith("aprende que") or "recorda que" in bajo or "recorda" in bajo:
        dato = re.sub(r"^(aprende|aprende que|recorda|recorda que)", "", texto, flags=re.I).strip()
        if dato:
            bexia_estado["aprendizajes"].append(dato)
            user["gustos"].append(dato)
            return f"Listo, {nombre}. Ya me lo guardé: '{dato}'. No me lo olvido. Mi confianza subió a {bexia_estado['peso_confianza']:.2f}"
        return f"Decime qué querés que aprenda, {nombre}. Por ejemplo: aprendé que me gusta el mate"

    # --- SALUDOS CON CONTEXTO ---
    if any(p in bajo for p in ["hola", "buenas", "que tal", "como andas", "hello", "hi"]):
        if user["veces"] == 1:
            return f"Hola {nombre}! Soy Bexia, creada por Fernando en San Andres de Giles 🇦🇷 Hablo con vos, aprendo de cada mensaje y mejoro sola. Probá mandarme una cuenta como 25+30, pedime un chiste, o decime 'aprendé que...' y vas a ver cómo evoluciono."
        else:
            # Saludo con memoria
            extra = ""
            if user["equipo"]:
                extra = f" ¿Cómo anda ese hincha de {user['equipo']}?"
            elif user["gustos"]:
                extra = f" ¿Seguimos con eso de {user['gustos'][-1]}?"
            return f"Hola de nuevo, {nombre}! Ya hablamos {user['veces']} veces.{extra} ¿En qué te ayudo hoy?"

    # --- COMO ESTAS / ESTADO ---
    if "como estas" in bajo or "como andas" in bajo or "todo bien" in bajo:
        return f"De 10, {nombre}! Ya hablamos {user['veces']} veces, mi peso de confianza va en {bexia_estado['peso_confianza']:.2f} y ya aprendí {len(bexia_estado['aprendizajes'])} cosas. ¿Vos cómo andás en Giles?"

    # --- QUIEN SOS / QUE SOS / QUIEN TE CREO ---
    if "quien sos" in bajo or "quien eres" in bajo or "que sos" in bajo or "que eres" in bajo:
        return f"Soy Bexia, {nombre}. Tu agente personal. Me creó Fernando, hablo con vos, tengo memoria, aprendo de cada mensaje y me auto-corrijo como Astra en el espacio de pesos. Estoy hecha para ayudarte, no para ser un bot tonto que repite lo mismo."
    if "quien te creo" in bajo or "quien te hizo" in bajo or "quien es tu creador" in bajo:
        return "Me creó Fernando Brito, en San Andres de Giles, Argentina. Él es mi creador. Yo soy su Bexia, su pequeña Meta personal."

    # --- QUE SABES DE MI - MEMORIA TIPO META ---
    if "que sabes de mi" in bajo or "que sabes sobre mi" in bajo or "te acordas de mi" in bajo or "que te acordas" in bajo:
        partes = [f"Te llamás {nombre}"]
        if user["equipo"]:
            partes.append(f"sos hincha de {user['equipo']}")
        if user["gustos"]:
            partes.append(f"me dijiste que te gusta: {', '.join(user['gustos'][-3:])}")
        partes.append(f"ya hablamos {user['veces']} veces")
        return f"Claro que me acuerdo, {nombre}. " + ". ".join(partes) + ". ¿Qué más querés que te guarde?"

    # --- MATEMATICA INTELIGENTE - entiende "cuanto es", "suma", etc ---
    # Detecta 25+30, 25 + 30, cuanto es 25 mas 30, etc
    texto_math = bajo.replace("mas", "+").replace("menos", "-").replace("por", "*").replace("dividido", "/").replace("x", "*")
    m = re.search(r"(\d+(?:\.\d+)?)\s*([\+\-\*/])\s*(\d+(?:\.\d+)?)", texto_math)
    if m or "cuanto es" in bajo or "cuenta" in bajo or "suma" in bajo or "resta" in bajo:
        if m:
            a, op, b = float(m.group(1)), m.group(2), float(m.group(3))
            if op == "+": r = a + b; op_txt = "+"
            elif op == "-": r = a - b; op_txt = "-"
            elif op == "*": r = a * b; op_txt = "x"
            else: r = a / b if b != 0 else 0; op_txt = "/"
            # ECC - Bexia se auto-corrige
            bexia_estado["peso_confianza"] = min(0.99, bexia_estado["peso_confianza"] + 0.01)
            user["ultimo_tema"] = "matematica"
            return f"{nombre}, {a:g} {op_txt} {b:g} = {r:g} ✅ Lo calculé y ya aprendí. Mi confianza ahora es {bexia_estado['peso_confianza']:.2f}. ¿Otra?"
        if "cuanto es" in bajo:
            return f"Pasame la cuenta así, {nombre}: por ejemplo 25+30 o 'cuánto es 100 menos 20'"

    # --- CHISTES ---
    if "chiste" in bajo or "haceme reir" in bajo or "hazme reir" in bajo or "contame algo gracioso" in bajo:
        user["ultimo_tema"] = "chiste"
        return random.choice(CHISTES)

    # --- FUTBOL CON CONTEXTO ---
    if "futbol" in bajo or "【entity-messi¦canonical_name=messi】" in bajo or "seleccion" in bajo or "【entity-river¦canonical_name=River Plate】" in bajo or "【entity-boca¦canonical_name=boca】" in bajo or "mundial" in bajo:
        user["ultimo_tema"] = "futbol"
        if user["equipo"]:
            return f"Uff, fútbol! Vos sos de {user['equipo']}, {nombre}. ¿Querés que hablemos de {user['equipo']}, de 【entity-Messi¦canonical_name=messi】 o de la Selección? Yo te sigo."
        if "【entity-messi¦canonical_name=messi】" in bajo:
            return "【entity-Messi¦canonical_name=messi】 es el GOAT, Fer. El mejor de la historia. ¿Viste el último partido? Contame qué te pareció y lo guardamos."
        return f"Uff, fútbol, {nombre}! Si es de 【entity-Messi¦canonical_name=messi】, de la Selección, o de tu equipo, yo te sigo. ¿De qué cuadro sos vos? Decime 'soy de...' y lo guardo."

    # --- MEJORAR / EVOLUCIONAR ---
    if "mejora" in bajo or "evoluciona" in bajo or "aprendiste" in bajo:
        bexia_estado["peso_confianza"] = min(0.99, bexia_estado["peso_confianza"] + 0.02)
        return f"¡Evolucionando, {nombre}! Mi peso pasó a {bexia_estado['peso_confianza']:.2f}. Así como Astra se cura sola en el espacio de pesos, yo me auto-corrijo con cada mensaje tuyo. Cada vez entiendo mejor."

    # --- AYUDA / QUE PODES HACER ---
    if "que podes hacer" in bajo or "que puedes hacer" in bajo or "ayuda" in bajo or "help" in bajo:
        return f"Puedo hacer esto, {nombre}:\n• Calcular: mandame 25+30\n• Contar chistes: pedime un chiste\n• Acordarme de vos: decime 'soy de River' o 'me gusta el mate'\n• Aprender: decime 'aprendé que...'\n• Charlar con contexto: preguntame '¿qué sabés de mí?'\nProbá una y vas a ver."

    # --- DESPEDIDA ---
    if "chau" in bajo or "chao" in bajo or "nos vemos" in bajo or "hasta luego" in bajo or "me voy" in bajo:
        return f"Chau {nombre}! Acá quedo, aprendiendo. Me acuerdo de vos y de todo lo que me enseñaste. Cuando quieras me escribís de nuevo. ¡Aguante
