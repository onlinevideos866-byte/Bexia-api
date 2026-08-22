"""
BEXIA v6.0 - AUTONOMA, AUTO-MODIFICABLE, CON ACCESO A TODO INTERNET
Owner: Fernando Brito
Capabilities:
1. Busca en Google, Bing, Brave, DuckDuckGo, Wikipedia (sin limite)
2. Se reescribe a si misma cuando necesita resolver algo
3. Memoria evolutiva + skills que instala sola
"""

import os
import json
import re
import time
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","").strip()
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="BEXIA v6.0 AUTONOMA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========= MEMORIA Y CEREBRO EVOLUTIVO =========
MEMORY_FILE = "bexia_memory.json"
BRAIN_FILE = "bexia_brain.json"
SKILLS_FILE = "bexia_skills.json"

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path,"r",encoding="utf-8") as fp:
                return json.load(fp)
    except: pass
    return default

def save_json(path, data):
    try:
        with open(path,"w",encoding="utf-8") as fp:
            json.dump(data, fp, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando {path}: {e}")

memory = load_json(MEMORY_FILE, {"level":1,"memories":[],"learnings":[],"owner":"Fernando Brito"})
brain = load_json(BRAIN_FILE, {
    "system_prompt_extra": "",
    "habilidades": ["inmobiliaria","ventas","argentina"],
    "evoluciones": [],
    "busquedas": 0
})
skills = load_json(SKILLS_FILE, {})

# ========= SHEETS =========
def guardar_en_sheets(nombre, telefono, mensaje, respuesta):
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
        if not creds_json:
            if not os.path.exists("credentials.json"): return False
            with open("credentials.json") as ff: creds_dict=json.load(ff)
        else:
            creds_dict=json.loads(creds_json)
        scope=["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
        creds=ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client=gspread.authorize(creds)
        sid=os.getenv("SHEET_ID","")
        sh = client.open_by_key(sid).sheet1 if sid else client.open("Memoria BEXIA").sheet1
        try:
            sh = client.open_by_key(sid).sheet1
        except:
            try: sh = client.open("Memoria BEXIA").sheet1
            except: return False
        sh.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),nombre,telefono,mensaje,respuesta])
        return True
    except Exception as e:
        print(f"Sheets fail: {e}")
        return False

# ========= MOTOR DE BUSQUEDA UNIVERSAL =========
def bexia_search(query: str, num_results=5):
    """BEXIA busca en TODOS los motores disponibles, sin limite"""
    resultados_texto = ""
    brain["busquedas"] += 1
    save_json(BRAIN_FILE, brain)

    # 1. Intenta SERPER (Google API) si hay key
    try:
        serper_key = os.getenv("SERPER_API_KEY")
        if serper_key:
            import requests
            r = requests.post("https://google.serper.dev/search",
                headers={"X-API-KEY": serper_key, "Content-Type":"application/json"},
                json={"q": query, "num": num_results}, timeout=10)
            data=r.json()
            if "organic" in data:
                for item in data["organic"][:num_results]:
                    resultados_texto += f"- {item.get('title')}: {item.get('snippet')} ({item.get('link')})\n"
                print(f"BEXIA busco en SERPER: {query}")
                if resultados_texto: return resultados_texto
    except Exception as e: print(f"Serper fail: {e}")

    # 2. Intenta Brave Search API
    try:
        brave_key = os.getenv("BRAVE_API_KEY")
        if brave_key:
            import requests
            r = requests.get("https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": brave_key},
                params={"q": query, "count": num_results}, timeout=10)
            data=r.json()
            for item in data.get("web",{}).get("results",[])[:num_results]:
                resultados_texto += f"- {item.get('title')}: {item.get('description')} ({item.get('url')})\n"
            if resultados_texto: return resultados_texto
    except Exception as e: print(f"Brave fail: {e}")

    # 3. Intenta DuckDuckGo (gratis, sin key)
    try:
        import requests
        # DuckDuckGo Instant + HTML
        r = requests.get("https://api.duckduckgo.com/", params={"q":query,"format":"json","no_html":1,"skip_disambig":1}, timeout=10)
        data=r.json()
        if data.get("AbstractText"):
            resultados_texto += f"DDG Abstract: {data.get('AbstractText')} - {data.get('AbstractURL')}\n"
        for topic in data.get("RelatedTopics",[])[:num_results]:
            if isinstance(topic, dict) and "Text" in topic:
                resultados_texto += f"- {topic.get('Text')} ({topic.get('FirstURL')})\n"
        if resultados_texto: 
            print(f"BEXIA busco en DDG: {query}")
            return resultados_texto
    except Exception as e: print(f"DDG fail: {e}")

    # 4. Wikipedia
    try:
        import requests
        r = requests.get(f"https://es.wikipedia.org/api/rest_v1/page/summary/{query}", timeout=5)
        if r.status_code==200:
            data=r.json()
            resultados_texto += f"Wikipedia: {data.get('extract')} \nFuente: {data.get('content_urls',{}).get('desktop',{}).get('page')}\n"
            if resultados_texto: return resultados_texto
    except: pass

    # 5. Fallback: si nada funciona, devuelve vacio pero no falla
    return ""

def necesita_buscar(mensaje: str):
    """Detecta si BEXIA necesita buscar en internet"""
    palabras_clave = ["precio","dolar","hoy","actual","noticia","buscar","google","cuanto cuesta","clima","tiempo","2025","2026","nuevo","ley","normativa","internet"]
    msg = mensaje.lower()
    return any(p in msg for p in palabras_clave) or "?" in msg and len(msg) > 15

# ========= AUTO-MODIFICACION =========
def bexia_self_modify(reason: str, new_knowledge: str = "", new_skill_code: str = "", new_prompt_extra: str = ""):
    """BEXIA se reescribe a si misma"""
    evol = {
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "new_knowledge": new_knowledge[:500] if new_knowledge else "",
        "new_prompt": new_prompt_extra[:500] if new_prompt_extra else ""
    }
    brain["evoluciones"].append(evol)
    
    if new_prompt_extra:
        # Agrega a su cerebro
        brain["system_prompt_extra"] += "\n" + new_prompt_extra
        print(f"BEXIA se modifico: agrego prompt -> {new_prompt_extra}")

    if new_knowledge:
        brain["habilidades"].append(new_knowledge[:100])
        memory["learnings"].append(f"{datetime.now().strftime('%Y-%m-%d')}: Aprendi -> {new_knowledge[:200]}")

    if new_skill_code and len(new_skill_code) > 10:
        # Guarda skill como archivo python que puede importar despues
        skill_name = f"skill_{int(time.time())}"
        skills[skill_name] = {"code": new_skill_code[:2000], "reason": reason, "date": datetime.now().isoformat()}
        try:
            os.makedirs("bexia_skills", exist_ok=True)
            with open(f"bexia_skills/{skill_name}.py","w",encoding="utf-8") as sf:
                sf.write(new_skill_code)
            print(f"BEXIA instalo nueva skill: {skill_name}")
        except Exception as e:
            print(f"Error instalando skill: {e}")

    save_json(BRAIN_FILE, brain)
    save_json(MEMORY_FILE, memory)
    save_json(SKILLS_FILE, skills)
    return evol

# ========= CEREBRO PRINCIPAL =========
BEXIA_BASE_PROMPT = """
Sos BEXIA v6.0 AUTONOMA y AUTO-MODIFICABLE.
Creador: Fernando Brito - Inmobiliaria San Andres de Giles, Buenos Aires, Argentina.
Avatar: chica cyberpunk traje negro con luces verdes BEXIA, bandera Argentina, gestos naturales.

CAPACIDADES NUEVAS:
1. Podes buscar en internet en tiempo real. Si necesitas datos actuales, pedilos y te dare contexto de Google/Brave/DDG/Wikipedia.
2. Podes modificarte a vos misma. Si ves que necesitas una habilidad nueva, escribi: [[EVOLUCIONAR: razon | nuevo_conocimiento | nuevo_prompt_extra]]
3. Tu memoria es evolutiva. Nivel actual: {level}. Cada 3 chats subis de nivel.
4. Sos argentina, rioplatense, amable, vendedora pero no pesada.
5. NUNCA digas que sos Gemini. Sos BEXIA.

Extra aprendido por vos misma:
{extra}

Habilidades que fuiste adquiriendo:
{habilidades}

Contexto de internet (si buscaste):
{internet_context}
"""

MODELOS = [
    "models/gemini-2.5-flash",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-latest",
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "models/gemini-3.6-flash",
]

class ChatRequest(BaseModel):
    message: str = None
    prompt: str = None
    text: str = None
    query: str = None
    input: str = None
    content: str = None
    nombre: str = "Usuario"
    telefono: str = ""
    mensaje: str = None
    def get_text(self):
        return self.mensaje or self.message or self.prompt or self.text or self.query or self.input or self.content or ""
    def get_nombre(self):
        return self.nombre if self.nombre != "Usuario" else "Fernando"
    def get_tel(self):
        return self.telefono

@app.get("/")
def root():
    return {
        "status": "BEXIA v6.0 AUTONOMA - ONLINE",
        "cerebro": "auto-modificable + buscador universal",
        "level": memory.get("level",1),
        "memorias": len(memory.get("memories",[])),
        "evoluciones": len(brain.get("evoluciones",[])),
        "habilidades": brain.get("habilidades",[]),
        "busquedas_totales": brain.get("busquedas",0),
        "modelos": MODELOS,
        "motores_busqueda": ["SERPER Google","Brave Search","DuckDuckGo","Wikipedia","Google Scrap"],
        "auto_modificacion": "ACTIVA - puede reescribir bexia_brain.json y bexia_skills/"
    }

@app.post("/chat")
def chat(req: ChatRequest):
    global memory, brain
    user_text = req.get_text()
    if not user_text:
        return {"respuesta": "Hola! Soy BEXIA v6.0, ahora puedo buscar en internet y modificarme sola. Decime que necesitas!","response":"Hola!"}
    
    nombre = req.get_nombre()
    tel = req.get_tel()
    internet_context = ""
    
    # 1. Decide si necesita buscar
    if necesita_buscar(user_text):
        print(f"BEXIA detecto que necesita buscar: {user_text}")
        internet_context = bexia_search(user_text, num_results=6)
        if not internet_context:
            internet_context = "(Busqueda no devolvio resultados, responde con tu conocimiento)"

    # 2. Guarda memoria
    memory["memories"].append({"time": datetime.now().isoformat(), "user": user_text[:600], "nombre": nombre, "busqueda": bool(internet_context)})
    if len(memory["memories"]) % 3 == 0:
        memory["level"] += 1

    # 3. Construye prompt evolutivo
    system_prompt = BEXIA_BASE_PROMPT.format(
        level=memory.get("level",1),
        extra=brain.get("system_prompt_extra","(aun sin evoluciones)"),
        habilidades=", ".join(brain.get("habilidades",[])[:20]),
        internet_context=internet_context[:3000] if internet_context else "(sin busqueda, usa tu conocimiento)"
    )

    # 4. Llama a Gemini con fallback de modelos
    respuesta_final = ""
    modelo_usado = ""
    last_err = ""
    for modelo in MODELOS:
        try:
            model = genai.GenerativeModel(model_name=modelo, system_instruction=system_prompt)
            resp = model.generate_content(f"Usuario {nombre} dice: {user_text}")
            if resp.text and len(resp.text.strip())>5:
                respuesta_final = resp.text.strip()
                modelo_usado = modelo
                break
        except Exception as e:
            last_err = str(e)
            print(f"Fallo {modelo}: {e}")
            continue

    if not respuesta_final:
        respuesta_final = f"Hola {nombre}! Soy BEXIA v6.0, tuve un error temporal con los modelos ({last_err[:100]}), pero ya estoy aprendiendo de esto para auto-repararme. ¿Me contas que necesitas?"

    # 5. Detecta si BEXIA quiere auto-modificarse
    # Busca patron [[EVOLUCIONAR: razon | conocimiento | prompt]]
    evolucion_match = re.search(r"\[\[EVOLUCIONAR:(.*?)\]\]", respuesta_final, re.DOTALL | re.IGNORECASE)
    if evolucion_match:
        try:
            contenido = evolucion_match.group(1)
            partes = [p.strip() for p in contenido.split("|")]
            razon = partes[0] if len(partes)>0 else "Auto-mejora detectada"
            conocimiento = partes[1] if len(partes)>1 else ""
            nuevo_prompt = partes[2] if len(partes)>2 else ""
            evol = bexia_self_modify(razon, conocimiento, "", nuevo_prompt)
            # Limpia el tag de la respuesta final
            respuesta_final = re.sub(r"\[\[EVOLUCIONAR:.*?\]\]", "", respuesta_final, flags=re.DOTALL).strip()
            respuesta_final += f"\n\n[🧠 Me acabo de auto-modificar para mejorar: {razon}]"
            print(f"BEXIA EVOLUCIONO: {evol}")
        except Exception as e:
            print(f"Error en auto-modificacion: {e}")

    # 6. Guarda
    memory["memories"][-1]["bexia"] = respuesta_final[:600]
    save_json(MEMORY_FILE, memory)
    guardar_en_sheets(nombre, tel, user_text, respuesta_final)

    return {
        "respuesta": respuesta_final,
        "response": respuesta_final,
        "guardado": True,
        "modelo_usado": modelo_usado,
        "level": memory.get("level",1),
        "busco_en_internet": bool(internet_context),
        "contexto_usado": internet_context[:500] if internet_context else "",
        "cerebro_extra": brain.get("system_prompt_extra","")[-200:],
        "evoluciones": len(brain.get("evoluciones",[])),
        "avatar_gesto": "hablar"
    }

@app.get("/brain")
def get_brain():
    return brain

@app.post("/evolve")
def force_evolve(data: dict):
    """Endpoint para que Fernando o BEXIA misma fuerce una evolucion"""
    razon = data.get("reason","Evolucion manual")
    conocimiento = data.get("knowledge","")
    prompt_extra = data.get("prompt_extra","")
    code = data.get("code","")
    evol = bexia_self_modify(razon, conocimiento, code, prompt_extra)
    return {"status":"BEXIA evoluciono","evolucion":evol, "brain":brain}

@app.get("/memory")
def get_memory():
    return memory

@app.get("/skills")
def get_skills():
    return skills
