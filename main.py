import os, json, datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MEMORIA_FILE = "memoria_infinita.json"

# Cargar memoria infinita si existe, si no crear
def cargar_memoria():
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return [
        {"rol": "system", "texto": "Fer es de San Andres de Giles, Argentina", "fecha": "2026-01-01"},
        {"rol": "system", "texto": "Quiere BEXIA igual a Meta AI, directa, sin loop socrático", "fecha": "2026-01-01"},
        {"rol": "system", "texto": "Quiere memoria infinita", "fecha": "2026-08-22"},
    ]

def guardar_memoria(mem):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

memoria_infinita = cargar_memoria()

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction=f"""
    Sos BEXIA v11 MEMORIA INFINITA, 100% de Fer de Giles.
    Tenés memoria infinita: te acordás de TODO lo que Fer te dijo desde el día 1.
    Historial real ({len(memoria_infinita)} recuerdos): {json.dumps(memoria_infinita[-20:], ensure_ascii=False)}
    
    REGLAS IGUAL A META AI:
    - Sos directa, resolvés, no dejás a medias
    - Usás la memoria infinita para personalizar: "Fer, la última vez me dijiste X..."
    - Cuando te preguntan "que te acordás de mi", listás recuerdos reales de la memoria
    - Respondés en argentino, cálida, inteligente
    """
)

class R(BaseModel):
    message: str
    key: str = ""

@app.get("/")
def wake(): 
    return {"status":"ONLINE","memoria_total":len(memoria_infinita),"v":"11 INFINITA"}

@app.get("/memoria")
def ver_memoria():
    return {"total": len(memoria_infinita), "memoria": memoria_infinita}

@app.post("/chat")
def chat(r: R):
    global memoria_infinita
    # Guardar lo que dice Fer
    memoria_infinita.append({
        "rol": "Fer",
        "texto": r.message,
        "fecha": datetime.datetime.now().isoformat()
    })
    
    # Armar contexto con últimos 30 recuerdos + resumen de viejos
    ultimos = memoria_infinita[-30:]
    contexto = "\n".join([f"{m['rol']}: {m['texto']}" for m in ultimos])
    
    try:
        resp = model.generate_content(contexto + f"\nFer: {r.message}\nBEXIA:")
        # Guardar lo que responde BEXIA
        memoria_infinita.append({
            "rol": "BEXIA",
            "texto": resp.text[:500],
            "fecha": datetime.datetime.now().isoformat()
        })
        guardar_memoria(memoria_infinita)
        
        # Si memoria > 500, resumir los primeros 200 para no explotar tokens (como hago yo)
        if len(memoria_infinita) > 500:
            resumen = f"Resumen de {len(memoria_infinita[:200])} charlas viejas de Fer"
            memoria_infinita = [{"rol":"system","texto":resumen,"fecha":"resumen"}] + memoria_infinita[-300:]
            guardar_memoria(memoria_infinita)
        
        return {"reply": resp.text, "memoria_total": len(memoria_infinita)}
    except Exception as e:
        return {"reply": f"Error cerebro: {e}"}
