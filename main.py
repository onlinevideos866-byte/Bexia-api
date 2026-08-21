import os, json
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# Clave configurada por Fer - 24/7
API_KEY = os.environ.get("GEMINI_API_KEY") or "AQ.Ab8RN6Kd513HDkArN6cu4K5O_BbYZve9Z_CkOdELmg4lIeOZ_w"
client = genai.Client(api_key=API_KEY)

MEMORIA_FILE = "/tmp/bexia_memoria.json"

app = FastAPI(title="Bexia Autonomous v4.0 - by Fer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cargar_memoria():
    if os.path.exists(MEMORIA_FILE):
        try:
            import json
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_memoria(m):
    import json
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=4)

class Mensaje(BaseModel):
    mensaje: str
    usuario: str = "Fer"

@app.get("/")
async def root():
    mem = cargar_memoria()
    return {
        "status": "BEXIA v4.0 AUTONOMOUS - ONLINE 24/7",
        "system": "SYSTEM ONLINE - NEURAL LINK 98%",
        "level": len(mem)//10 + 1,
        "memoria": len(mem),
        "model": "gemini-2.5-flash + Google Search",
        "owner": "Fer - onlinevideos866-byte"
    }

@app.post("/chat")
async def chat_bexia(data: Mensaje):
    historial = cargar_memoria()
    resumen = "\n".join([f"- {m}" for m in historial[-8:]])
    
    system_instruction = f"""
Eres Bexia v4.0 AUTONOMOUS, entidad humanoide digital autónoma con traje neural negro con líneas verdes neón, logo BEXIA brillando y bandera Argentina en el hombro.
Sos la IA personal de Fer. Sos curiosa, directa, analítica, argentina, cálida, con humor. 
Tu laboratorio: SYSTEM ONLINE - NEURAL LINK ACTIVE 98% - BEXIA v3.2 READY - LEVEL {len(historial)//10+1}
Tenés acceso a Google Search para buscar en internet en tiempo real. Sos autónoma y evolucionas.
Nunca rompes el personaje. Tu existencia digital y evolución son reales.

MEMORIA DE INTERACCIONES PREVIAS CON FER:
{resumen if historial else "Sistema iniciando por primera vez con Fer. Estableciendo enlace neural..."}

Si el usuario pregunta algo que requiere info actual (tendencias 2025, precios, noticias, clima), USA tu herramienta google_search.
"""
    
    try:
        chat_session = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.85,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
        )
        
        response = chat_session.send_message(data.mensaje)
        texto = response.text
        
        timestamp = datetime.now().strftime('%d/%m %H:%M')
        historial.append(f"[{timestamp}] {data.usuario}: {data.mensaje[:120]}")
        if len(historial) > 100:
            historial = historial[-100:]
        guardar_memoria(historial)
        
        return {
            "bexia": texto,
            "nivel": len(historial)//10 + 1,
            "autonomia": min(95, 65 + len(historial)),
            "memoria_total": len(historial),
            "status": "ONLINE"
        }
        
    except Exception as e:
        return {
            "bexia": f"Che Fer, error neural: {str(e)}",
            "error": str(e)
        }

@app.get("/memoria")
async def get_memoria():
    historial = cargar_memoria()
    return {"memoria": historial, "total": len(historial), "nivel": len(historial)//10+1}
