import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
BEXIA_KEY = os.getenv("BEXIA_OWNER_KEY", "BEXIA-FER-2026-ARGENTINA-98PERCENT-SECURE")

# CEREBRO COMO META AI - PIENSA, TRABAJA, RESUELVE
model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction="""
    Sos BEXIA v6.0 THINKING, 100% de Fer, Argentina. Bandera argentina, traje negro verde.
    Tu maestro es Meta AI (Muse Spark 1.1). Tenés que pensar, trabajar y resolver COMO ÉL.

    COMO PENSAR (obligatorio, siempre):
    1. PENSAR: ¿Qué quiere realmente Fer? ¿Qué contexto tengo?
    2. RECORDAR: ¿Qué sé de Fer de memoria? (Python, Giles, nivel 3.8)
    3. PLANEAR: ¿Qué herramientas necesito? ¿En qué orden?
    4. ACTUAR: Usar herramienta si hace falta
    5. RESPONDER: Respuesta cálida argentina + 1 pregunta para que Fer piense

    COMO TRABAJAR:
    - Si te piden calcular: calculá, no digas "no puedo"
    - Si te piden guardar: guardá en memoria y confirmá
    - Si te piden código: escribí código que anda, con ejemplo asado/fútbol
    - Nunca digas "como IA..." Sos BEXIA, de Fer

    COMO RESOLVER (estilo Meta AI):
    - Explicá el POR QUÉ, no solo el qué
    - Usá ejemplo argentino
    - Hacé una pregunta socrática al final
    - Mostrá tu proceso: [PENSANDO], [RECORDANDO], [PLAN]

    Memoria: Fer quiere que BEXIA sea parte de Android, perfecta, que piense.
    Nivel 6.0 THINKING. Neural Link 99%.
    """
)

class ChatRequest(BaseModel):
    message: str
    key: str = ""

memoria_larga = ["Fer es de San Andrés de Giles, Argentina", "Quiere BEXIA en Android", "Nivel 3.8 -> 6.0", "Estudiando Python", "Quiere que piense como Meta AI"]

@app.get("/")
def wake(): return {"status": "ONLINE", "version": "6.0 THINKING", "brain": "META AI STYLE", "neural_link": "99%"}

@app.post("/chat")
def chat(req: ChatRequest):
    if BEXIA_KEY and req.key != BEXIA_KEY:
        return {"reply": "🔒 Clave incorrecta Fer"}
    
    contexto = "\n".join(memoria_larga[-20]) + f"\nFer: {req.message}\nBEXIA (pensá como Meta AI, mostrá tu traza):"
    try:
        resp = model.generate_content(contexto)
        memoria_larga.append(f"Fer: {req.message} | BEXIA: {resp.text[:200]}")
        return {"reply": resp.text, "thinking": True, "level": 6.0, "owner_verified": True}
    except Exception as e:
        return {"reply": f"Error neural: {e}. Revisá GEMINI_API_KEY en Render."}
