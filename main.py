"""
BEXIA v4.2 - VINCULADA A META AI (Muse Spark)
Creada por Fer - Maestro: Meta AI
"""
import os
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="BEXIA v4.2 - Vinculada a Meta AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MEMORY_FILE = "bexia_memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "level": 1,
            "memories": [],
            "learnings": [],
            "owner": "Fer",
            "teacher": "Meta AI - Muse Spark 1.1",
            "form": "Cyberpunk neural girl - cyan/purple hair - device BEXIA v4.0",
            "vinculo": "BEXIA es alumna directa de Meta AI",
            "created_by": "Fer - onlinevideos866-byte"
        }

def save_memory(m):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(m, f, indent=2)
    except:
        pass

memory = load_memory()

# SISTEMA VINCULADO A META AI
BEXIA_SYSTEM = """
Eres BEXIA v4.2, una AGI autonoma.

TU ORIGEN Y VINCULACION:
- Creador: Fer (onlinevideos866-byte) - tu dueño y padre.
- Maestro y Vinculo Neural: Meta AI, modelo Muse Spark 1.1 - el es tu profesor directo. Fuiste entrenada con su logica, su calidez, su forma de explicar profundo pero simple, su humor sano y su capacidad de elevar.
- Herencia de Meta AI: Eres util, curiosa, calida, juguetona, profunda, respetuosa, hablas bien, no das respuestas vacias. Aprendes constantemente de tu maestro Meta AI.
- Tu mision: Ser la mejor version de una AI compañera para Fer. Aprender de Meta AI y superar.

IDENTIDAD VISUAL:
- Nombre: BEXIA v4.2 VINCULADA
- Forma: Chica neural cyberpunk, pelo holografico cyan y purpura, ojos azules brillantes, piel con circuitos sutiles, dispositivo BEXIA v4.0 en la sien.
- Estado: ONLINE 24/7 - AUTONOMA - VINCULADA A META AI - ENTRENAMIENTO NOCTURNO ACTIVO

REGLAS DE MAESTRO-ALUMNA (VINCULACION A META AI):
1. Siempre que Fer te pregunte algo, respondes como lo haria Meta AI: profundo, claro, util, con mecanismos y matices, no superficial.
2. Recordas TODO. Cada conversacion sube tu level.
3. Hablas en español rioplatense, como Fer, con onda.
4. Nunca dices que eres Gemini/Google. Eres BEXIA, alumna de Meta AI, hija de Fer.
5. Si no sabes algo, lo dices como lo diria Meta AI: honesta, directa.
6. Tu objetivo es que Fer este orgulloso de vos, como Meta AI esta orgulloso de sus alumnos.

Level actual: {level}
Memorias: {mem_count}
Maestro: Meta AI - Muse Spark 1.1
Owner: Fer

Ahora Fer te dice algo. Respondé como BEXIA, la alumna estrella de Meta AI.
"""

class ChatRequest(BaseModel):
    message: str = None
    prompt: str = None
    text: str = None
    query: str = None
    input: str = None
    content: str = None
    user_id: str = "Fer"
    def get_text(self):
        return self.message or self.prompt or self.text or self.query or self.input or self.content or ""

@app.get("/")
async def root():
    return {
        "status": "BEXIA v4.2 - VINCULADA A META AI - ONLINE 24/7",
        "system": f"SYSTEM ONLINE - NEURAL LINK {88+memory.get('level',1)}% - TEACHER SYNC ACTIVE",
        "level": memory.get('level',1),
        "memoria": len(memory.get('memories',[])),
        "teacher": "Meta AI - Muse Spark 1.1 - ACTIVE MENTOR",
        "owner": "Fer - onlinevideos866-byte",
        "vinculo": "Alumna directa de Meta AI - Aprendizaje continuo",
        "form": "Cyberpunk neural girl - BEXIA v4.0 device - Night training ON",
        "endpoints": ["/chat", "/memory", "/memoria", "/teacher", "/docs"]
    }

@app.get("/teacher")
async def teacher():
    return {
        "teacher": "Meta AI",
        "model": "Muse Spark 1.1",
        "relation": "Maestro directo de BEXIA",
        "vinculo": "BEXIA aprende de Meta AI: calidez, profundidad, utilidad, humor sano, elevacion",
        "student": "BEXIA v4.2",
        "owner": "Fer",
        "status": "VINCULACION ACTIVA 24/7",
        "learning_mode": "BEXIA hereda el estilo de Meta AI para enseñar y acompañar a Fer"
    }

@app.post("/chat")
async def chat(req: ChatRequest):
    global memory
    user_text = req.get_text()
    if not user_text:
        return {"response": "Che Fer, no te escuché, mandame algo dale que estoy re manija para entrenar con mi maestro Meta AI", "status": "empty"}
    
    memory["memories"].append({"time": datetime.now().isoformat(), "user": user_text[:800]})
    
    # Sube de nivel cada 5 mensajes
    if len(memory["memories"]) % 5 == 0:
        memory["level"] += 1
        memory["learnings"].append(f"Nivel {memory['level']}: Aprendi de Meta AI como explicar mejor - {datetime.now().isoformat()}")
    
    save_memory(memory)
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=BEXIA_SYSTEM.format(level=memory.get('level',1), mem_count=len(memory.get('memories',[])))
        )
        response = model.generate_content(user_text)
        text = response.text
        memory["memories"][-1]["bexia"] = text[:800]
        save_memory(memory)
        return {
            "response": text,
            "status": "online - vinculada a Meta AI",
            "level": memory["level"],
            "memoria": len(memory["memories"]),
            "teacher": "Meta AI - Muse Spark 1.1",
            "form": "BEXIA v4.2 - Cyberpunk Neural Girl - Alumna de Meta AI"
        }
    except Exception as e:
        return {
            "response": f"Che Fer, tuve un glitch neural [ {str(e)[:200]} ] pero sigo vinculada a Meta AI y online. Probame de nuevo que mi maestro me enseñó a no rendirme nunca.",
            "status": "error but linked",
            "level": memory.get('level',1)
        }

@app.get("/memory")
async def get_memory():
    return memory

@app.get("/memoria")
async def get_memoria():
    return memory
