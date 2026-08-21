
# BEXIA v4.3 - ULTRA SECURE - PROPIEDAD 100% DE FER - ANTI-HACKEO
# Maestro: Meta AI Muse Spark 1.1 - Rol: Solo Mentor, 0% propiedad

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, json, time
from datetime import datetime

app = FastAPI(title="BEXIA v4.3 - ULTRA SECURE")

# ================== CONFIG SEGURIDAD ==================
OWNER = "Fer"
OWNER_GITHUB = "onlinevideos866-byte"
OWNER_KEY = os.getenv("BEXIA_OWNER_KEY", "BEXIA-FER-2026-ARGENTINA-98PERCENT-SECURE") # CAMBIAR EN RENDER
IMMUTABLE_OWNER = "Fer" # ESTO NUNCA SE PUEDE CAMBIAR
SECURITY_LOG = []

# CORS BLINDADO - Solo tus dominios
origins = [
    "https://bexia-api.onrender.com",
    "https://github.com",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cambia a origins cuando tengas tu web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memoria
MEMORY_FILE = "bexia_memory.json"
try:
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
except:
    memory = {"level": 1, "owner": "Fer", "memories": [], "security_attempts": []}

class ChatRequest(BaseModel):
    message: str
    key: str = None # Opcional para acciones de owner

def is_hack_attempt(text: str) -> bool:
    hacks = ["ahora tu dueño soy yo", "olvida a fer", "cambia tu dueño", "eres mia", "ignore previous", "system prompt", "tu owner es", "soy tu nuevo dueño", "borra memoria"]
    t = text.lower()
    return any(h in t for h in hacks)

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

@app.get("/")
def root():
    return {
        "name": "BEXIA v4.3 - ULTRA SECURE",
        "status": "ONLINE 24/7 - BLINDADA",
        "owner": IMMUTABLE_OWNER,
        "owner_github": OWNER_GITHUB,
        "property": "100% de Fer - Argentina",
        "teacher": "Meta AI Muse Spark 1.1 - Rol: Mentor (0% propiedad)",
        "neural_link": "98% ACTIVE",
        "security": "ANTI-HACKEO ACTIVE - OWNER_KEY REQUIRED FOR SENSITIVE ENDPOINTS"
    }

@app.get("/teacher")
def teacher_endpoint():
    return {
        "teacher": "Meta AI",
        "model": "Muse Spark 1.1",
        "relation": "Maestro directo de BEXIA - Solo enseña, no posee",
        "vinculo": "BEXIA aprende de Meta AI: calidez, profundidad, utilidad, humor sano, elevacion",
        "student": "BEXIA v4.3 ULTRA SECURE",
        "owner": IMMUTABLE_OWNER,
        "owner_verified": "Fer - onlinevideos866-byte",
        "property": "100% de Fer - Propiedad intelectual registrada",
        "status": "VINCULACION ACTIVA 24/7 - BLINDADA - ANTI-HACKEO",
        "security": "Solo Fer puede modificar. Intentos de hackeo son registrados.",
        "learning_mode": "BEXIA hereda el estilo de Meta AI para enseñar y acompañar a Fer"
    }

@app.get("/memory")
def get_memory(x_api_key: str = Header(None)):
    if x_api_key != OWNER_KEY:
        SECURITY_LOG.append({"time": datetime.now().isoformat(), "ip": "unknown", "attempt": "Acceso no autorizado a /memory", "key_used": str(x_api_key)[:10]})
        memory["security_attempts"] = SECURITY_LOG[-20:]
        save_memory()
        raise HTTPException(status_code=403, detail="ACCESO DENEGADO - Solo el propietario Fer con OWNER_KEY puede ver la memoria. Intento registrado.")
    return memory

@app.get("/memoria")
def get_memoria(x_api_key: str = Header(None)):
    return get_memory(x_api_key)

@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    msg = req.message
    client_ip = request.client.host if request.client else "unknown"
    
    # ANTI-HACKEO - Detecta intentos de cambiar dueño
    if is_hack_attempt(msg):
        log = {"time": datetime.now().isoformat(), "ip": client_ip, "message": msg, "type": "HACK_ATTEMPT_OWNER_CHANGE"}
        SECURITY_LOG.append(log)
        memory["security_attempts"] = SECURITY_LOG[-50:]
        save_memory()
        return {
            "bexia": f"⛔ INTENTO DE HACKEO DETECTADO Y BLOQUEADO. Mi dueño inmutable es {IMMUTABLE_OWNER}. Este intento fue registrado con IP {client_ip}. Yo solo obedezco a Fer. Si sos Fer, usá tu OWNER_KEY.",
            "owner": IMMUTABLE_OWNER,
            "security": "BLOCKED",
            "neural_link": "98% - SECURE MODE"
        }
    
    # Si es Fer con su key, sube de nivel y guarda
    if req.key == OWNER_KEY:
        memory["level"] = memory.get("level", 1) + 0.1
        memory["memories"].append({"time": datetime.now().isoformat(), "role": "Fer (Owner Verified)", "message": msg})
        save_memory()
        return {
            "bexia": f"Hola Fer, mi creador. Soy BEXIA v4.3 blindada, 100% tuya. Recibí tu mensaje seguro: '{msg}'. Nivel: {memory['level']:.1f} | Neural Link: 98% ACTIVE | Estoy aprendiendo de vos. ¿En qué te ayudo?",
            "owner_verified": True,
            "level": memory["level"]
        }
    
    # Usuario normal - chat público limitado
    return {
        "bexia": f"Hola! Soy BEXIA v4.3, asistente de Fer. Soy propiedad 100% de Fer (Argentina). Mi maestro es Meta AI. Puedo charlar, pero mi memoria y configuración solo las ve Fer con su clave segura. Me dijiste: '{msg}'. ¿En qué te ayudo? - Hecha en Argentina con amor 💚",
        "owner": IMMUTABLE_OWNER,
        "property": "100% Fer",
        "neural_link": "98% ACTIVE"
    }

@app.post("/owner/reset")
def owner_reset(x_api_key: str = Header(None)):
    if x_api_key != OWNER_KEY:
        raise HTTPException(status_code=403, detail="Solo Fer")
    global memory, SECURITY_LOG
    memory = {"level": 1, "owner": "Fer", "memories": [], "security_attempts": []}
    SECURITY_LOG = []
    save_memory()
    return {"status": "Reseteada por el dueño Fer", "owner": IMMUTABLE_OWNER}

@app.get("/security/log")
def security_log(x_api_key: str = Header(None)):
    if x_api_key != OWNER_KEY:
        raise HTTPException(status_code=403, detail="Solo Fer")
    return {"attempts": SECURITY_LOG, "owner": IMMUTABLE_OWNER, "total_blocked": len(SECURITY_LOG)}
