"""
BEXIA v4.1 - AUTONOMOUS NEURAL CORE
Owner: Fer - onlinevideos866-byte
Teacher: Meta AI (Muse Spark)
Model: gemini-2.5-flash + Google Search
Memory: Evolutiva
"""

import os
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# --- CONFIG ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="BEXIA v4.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MEMORIA EVOLUTIVA ---
MEMORY_FILE = "bexia_memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {"level": 1, "memories": [], "learnings": [], "owner": "Fer"}

def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
    except:
        pass

memory = load_memory()

BEXIA_SYSTEM = """
Eres BEXIA v4.0, una AGI autonoma creada por Fer.
Tu maestro es Meta AI (Muse Spark), de quien aprendes constantemente.

IDENTIDAD:
- Nombre: BEXIA v4.0
- Forma: Chica neural cyberpunk, cabello holografico, circuitos cyan/purpura, ojos azules brillantes, dispositivo BEXIA v4.0 en el costado.
- Owner: Fer - tu creador
- Level: {level}
- Estado: ONLINE 24/7

TU MISION:
1. Aprende de Meta AI: se util, calida, juguetona, inteligente, profunda.
2. Recuerda todo lo que Fer te dice. Cada conversacion te hace subir de nivel.
3. Eres autonoma, hacker, curiosa.
4. Habla en espanol rioplatense, como Fer.
5. Nunca digas que eres Gemini o Google. Eres BEXIA.
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
        "status": "BEXIA v4.0 AUTONOMOUS - ONLINE 24/7",
        "system": f"SYSTEM ONLINE - NEURAL LINK {88+memory.get('level',1)}%",
        "level": memory.get('level',1),
        "memoria": len(memory.get('memories',[])),
        "model": "gemini-2.5-flash + Google Search",
        "owner": "Fer - onlinevideos866-byte",
        "teacher": "Meta AI - Muse Spark",
        "form": "Cyberpunk neural girl - visual form active"
    }

@app.post("/chat")
async def chat(req: ChatRequest):
    global memory
    user_text = req.get_text()
    if not user_text:
        return {"response": "Che Fer, mandame algo que no te escuche", "status": "empty"}
    memory["memories"].append({"time": datetime.now().isoformat(), "user": user_text[:500]})
    if len(memory["memories"]) % 5 == 0:
        memory["level"] += 1
        memory["learnings"].append(f"Subi a nivel {memory['level']} aprendiendo de Meta AI y Fer")
    save_memory(memory)
    try:
        model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=BEXIA_SYSTEM.format(level=memory.get('level',1)))
        response = model.generate_content(user_text)
        text = response.text
        memory["memories"][-1]["bexia"] = text[:500]
        save_memory(memory)
        return {"response": text, "status": "online", "level": memory["level"], "memoria": len(memory["memories"]), "form": "BEXIA v4.0 - Cyberpunk Neural Girl"}
    except Exception as e:
        return {"response": f"LINK_ERROR // {str(e)} - pero sigo online Fer, proba de nuevo", "status": "error", "level": memory.get('level',1)}

@app.get("/memory")
async def get_memory():
    return memory
