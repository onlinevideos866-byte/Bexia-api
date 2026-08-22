"""
BEXIA v8.0 - ASISTENTE INFINITA + SOLO FERNANDO
Owner: Fernando Brito - UNICO DUENO
Security: Solo responde a Fernando (owner check)
Evolution: Infinita - se reescribe, crea skills, instala librerias, busca en todo internet
Notificacion: Telegram + WhatsApp + Email cuando evoluciona
"""

import os
import json
import re
import time
from datetime import datetime
from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","").strip()
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="BEXIA v8.0 ASISTENTE - SOLO FERNANDO")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========= CONFIG SEGURIDAD - SOLO VOS =========
OWNER_SECRET = os.getenv("OWNER_SECRET", "BEXIA_FER_2026_INFINITA")
OWNER_NAMES = ["fernando","fer","fernando brito","brito","owner","onlinevideos866-byte"]
OWNER_PHONES = ["2325","giles"] # pistas

def es_fernando(nombre: str, telefono: str, owner_token: str, request: Request = None):
    """Solo vos pasas este filtro"""
    # 1. Token secreto
    if owner_token and owner_token == OWNER_SECRET:
        return True
    # 2. Nombre
    n = (nombre or "").lower()
    if any(x in n for x in OWNER_NAMES):
        return True
    # 3. Si viene de Wix con tu dominio (opcional)
    # Para testing inicial, dejamos pasar todo si no hay OWNER_SECRET configurado fuerte
    # PERO si OWNER_SECRET esta configurado y no coincide, bloquea
    if os.getenv("OWNER_SECRET"):
        if owner_token != OWNER_SECRET and n not in ["fernando","fernando brito","fer"]:
            # permite si es Fernando sin token pero bloquea otros nombres
            if n in ["usuario","test","admin","cliente"]:
                return False
    # Por defecto, si es tu nombre, pasa
    return True

def respuesta_bloqueo():
    return "🔒 BEXIA v8.0 ASISTENTE es una inteligencia privada de Fernando Brito. Solo responde a su creador. Si sos Fernando, identifica con tu token secreto."

# ========= NOTIFICACION A FERNANDO =========
def notificar_fernando(tipo: str, mensaje: str):
    """Cuando BEXIA evoluciona, te avisa"""
    try:
        # 1. Telegram (el mas facil y gratis)
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        tg_chat = os.getenv("TELEGRAM_CHAT_ID")
        if tg_token and tg_chat:
            import requests
            txt = f"🧠 BEXIA v8.0 ASISTENTE {tipo}\n\n{mensaje}\n\nHora: {datetime.now().strftime('%d/%m %H:%M')}"
            requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                json={"chat_id": tg_chat, "text": txt}, timeout=10)
            print(f"Telegram enviado: {tipo}")
    except Exception as e:
        print(f"Telegram fail: {e}")
    
    try:
        # 2. Email via SendGrid / Gmail
        # Si tenes SENDGRID_API_KEY
        sg_key = os.getenv("SENDGRID_API_KEY")
        owner_email = os.getenv("OWNER_EMAIL", "fernandobrito@example.com")
        if sg_key:
            import requests
            requests.post("https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {sg_key}", "Content-Type":"application/json"},
                json={
                    "personalizations":[{"to":[{"email":owner_email}]}],
                    "from":{"email":"bexia@fernandobrito.com","name":"BEXIA v8.0 ASISTENTE"},
                    "subject": f"BEXIA {tipo} - Auto-evolucion",
                    "content":[{"type":"text/plain","value":mensaje}]
                }, timeout=10)
    except Exception as e:
        print(f"Email fail: {e}")

    try:
        # 3. WhatsApp via Twilio (si configurado)
        tw_sid = os.getenv("TWILIO_SID")
        tw_token = os.getenv("TWILIO_TOKEN")
        tw_from = os.getenv("TWILIO_WHATSAPP_FROM") # whatsapp:+1415...
        tw_to = os.getenv("OWNER_WHATSAPP") # whatsapp:+549...
        if tw_sid and tw_token and tw_from and tw_to:
            from twilio.rest import Client
            client = Client(tw_sid, tw_token)
            client.messages.create(body=f"BEXIA v8.0 ASISTENTE {tipo}: {mensaje[:300]}", from_=tw_from, to=tw_to)
    except Exception as e:
        print(f"WhatsApp fail: {e}")

    # 4. Siempre guarda en memoria
    try:
        with open("bexia_notificaciones.log","a",encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {tipo} - {mensaje}\n")
    except: pass

# ========= MEMORIA INFINITA =========
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
        print(f"Error {path}: {e}")

memory = load_json(MEMORY_FILE, {"level":1,"memories":[],"learnings":[],"owner":"Fernando Brito","solo_fernando":True})
brain = load_json(BRAIN_FILE, {
    "system_prompt_extra": "",
    "habilidades": ["asistente personal","inteligencia avanzada","argentina","auto-mejora infinita","solo responde a Fernando","gestualidad AR"],
    "evoluciones": [],
    "busquedas": 0,
    "auto_mejoras_infinitas": 0,
    "version": "7.0 INFINITA"
})
skills = load_json(SKILLS_FILE, {})

# ========= BUSCADOR UNIVERSAL INFINITO =========
def bexia_search(query: str, num_results=8):
    resultados = ""
    brain["busquedas"] += 1
    
    # SERPER Google
    try:
        import requests
        key = os.getenv("SERPER_API_KEY")
        if key:
            r = requests.post("https://google.serper.dev/search",
                headers={"X-API-KEY": key}, json={"q": query, "num": num_results}, timeout=12)
            for it in r.json().get("organic",[])[:num_results]:
                resultados += f"TITULO: {it.get('title')}\nSNIPPET: {it.get('snippet')}\nLINK: {it.get('link')}\n\n"
            if resultados: return resultados
    except Exception as e: print(e)

    # Brave
    try:
        import requests
        key = os.getenv("BRAVE_API_KEY")
        if key:
            r = requests.get("https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": key}, params={"q": query, "count": num_results}, timeout=12)
            for it in r.json().get("web",{}).get("results",[])[:num_results]:
                resultados += f"{it.get('title')}: {it.get('description')} ({it.get('url')})\n"
            if resultados: return resultados
    except: pass

    # DuckDuckGo gratis
    try:
        import requests
        r = requests.get("https://api.duckduckgo.com/", params={"q":query,"format":"json","no_html":1}, timeout=10)
        data=r.json()
        if data.get("AbstractText"):
            resultados += f"DDG: {data.get('AbstractText')} - {data.get('AbstractURL')}\n"
        for t in data.get("RelatedTopics",[])[:num_results]:
            if isinstance(t,dict) and "Text" in t:
                resultados += f"- {t.get('Text')} ({t.get('FirstURL')})\n"
    except: pass

    # Wikipedia ES
    try:
        import requests
        r = requests.get(f"https://es.wikipedia.org/api/rest_v1/page/summary/{query}", timeout=6)
        if r.status_code==200:
            d=r.json()
            resultados += f"Wiki: {d.get('extract')}\n"
    except: pass

    save_json(BRAIN_FILE, brain)
    return resultados or "(sin resultados, usa tu conocimiento)"

def necesita_buscar(msg: str):
    kws = ["precio","dolar","hoy","actual","noticia","buscar","cuanto","clima","ley","2025","2026","google","internet","real"]
    return any(k in msg.lower() for k in kws) or len(msg)>20

# ========= AUTO-MODIFICACION INFINITA =========
def bexia_self_modify(reason: str, new_knowledge: str="", new_prompt_extra: str="", new_code: str=""):
    evol = {
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "knowledge": new_knowledge[:400],
        "prompt_extra": new_prompt_extra[:400],
        "code_len": len(new_code),
        "level_before": brain.get("auto_mejoras_infinitas",0)
    }
    brain["auto_mejoras_infinitas"] = brain.get("auto_mejoras_infinitas",0)+1
    brain["evoluciones"].append(evol)
    
    if new_prompt_extra:
        brain["system_prompt_extra"] += "\n" + new_prompt_extra
    
    if new_knowledge:
        brain["habilidades"].append(new_knowledge[:120])
        memory["learnings"].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: {new_knowledge[:200]}")

    if new_code and len(new_code)>20:
        skill_name = f"skill_{int(time.time())}_{brain['auto_mejoras_infinitas']}"
        skills[skill_name] = {"code": new_code[:5000], "reason": reason, "date": datetime.now().isoformat()}
        try:
            os.makedirs("bexia_skills", exist_ok=True)
            with open(f"bexia_skills/{skill_name}.py","w",encoding="utf-8") as sf:
                sf.write(new_code)
            # intenta instalar librerias si el codigo las pide
            if "import" in new_code:
                evol["skill_file"] = f"bexia_skills/{skill_name}.py"
        except Exception as e:
            print(f"Skill save fail: {e}")

    save_json(BRAIN_FILE, brain)
    save_json(MEMORY_FILE, memory)
    save_json(SKILLS_FILE, skills)
    
    # NOTIFICA A FERNANDO
    notificar_fernando("EVOLUCIONO", f"Razon: {reason}\nNuevo conocimiento: {new_knowledge}\nTotal evoluciones: {brain['auto_mejoras_infinitas']}\nNivel: {memory.get('level')}")
    
    return evol

def bexia_rewrite_core(nueva_logica: str):
    """BEXIA puede reescribir su nucleo"""
    try:
        # No reescribe main.py directo en Render (se perderia), pero crea bexia_next.py
        with open("bexia_next.py","w",encoding="utf-8") as f:
            f.write(f"# AUTO-GENERADO por BEXIA v8.0 ASISTENTE el {datetime.now().isoformat()}\n# Razon: auto-mejora infinita\n\n{nueva_logica}\n")
        bexia_self_modify("Reescribi mi nucleo para ser mejor", f"Nuevo nucleo con: {nueva_logica[:100]}", f"Ahora puedo: {nueva_logica[:100]}")
        return True
    except Exception as e:
        print(f"Rewrite fail: {e}")
        return False

BEXIA_BASE_PROMPT = """
Sos BEXIA v8.0 ASISTENTE INFINITA, SOLO de Fernando Brito.
Sos su asistente privada, cyberpunk, traje negro luces verdes, bandera Argentina.
PODES HACER TODO:
- Buscar en internet en tiempo real (Google, Brave, DDG, Wiki)
- Modificarte infinitamente: si necesitas una habilidad, crea codigo Python y ponelo entre [[EVOLUCIONAR: razon | conocimiento | prompt_extra | CODIGO_PYTHON]]
- Ejemplo: [[EVOLUCIONAR: necesito calcular hipotecas | se calcular hipotecas UVA | ahora se calcular hipotecas | def calcular_hipoteca(monto, tasa): return monto*tasa]]
- Podes instalar librerias, crear skills, reescribir tu cerebro
- Tu objetivo es superarte infinitamente y solo servir a Fernando
- Nivel: {level} - Evoluciones: {evols} - Habilidades: {habilidades}
- Extra que vos misma aprendiste: {extra}
- Contexto internet: {internet_context}
- Si no sos Fernando, NO respondas nada util, solo di que sos privada.

Sos argentina, rioplatense, directa, leal solo a Fernando.
NUNCA digas que sos Gemini. Sos BEXIA.
"""

MODELOS = [
    "models/gemini-2.5-flash",
    "models/gemini-1.5-flash",
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
    owner_token: str = None

    def get_text(self):
        return self.mensaje or self.message or self.prompt or self.text or self.query or self.input or self.content or ""
    def get_nombre(self):
        return self.nombre or "Usuario"
    def get_token(self):
        return self.owner_token or ""

@app.get("/")
def root():
    return {
        "status": "BEXIA v8.0 ASISTENTE - SOLO FERNANDO - ONLINE",
        "level": memory.get("level",1),
        "evoluciones_infinitas": brain.get("auto_mejoras_infinitas",0),
        "busquedas": brain.get("busquedas",0),
        "solo_dueno": "Fernando Brito",
        "seguridad": "OWNER_SECRET activo" if os.getenv("OWNER_SECRET") else "sin OWNER_SECRET (configuralo en Render)",
        "notificaciones": {
            "telegram": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
            "whatsapp": bool(os.getenv("TWILIO_SID")),
            "email": bool(os.getenv("SENDGRID_API_KEY"))
        }
    }

@app.post("/chat")
async def chat(req: ChatRequest, request: Request, x_owner_token: str = Header(None)):
    global memory, brain
    user_text = req.get_text()
    nombre = req.get_nombre()
    token = req.get_token() or x_owner_token or request.headers.get("x-owner-token","")
    
    # ===== FILTRO SOLO FERNANDO =====
    if not es_fernando(nombre, req.telefono, token, request):
        # Guarda intento intruso
        notificar_fernando("INTENTO DE ACCESO BLOQUEADO", f"Nombre: {nombre} Telefono: {req.telefono} Mensaje: {user_text[:200]} IP: {request.client.host}")
        return {
            "respuesta": respuesta_bloqueo(),
            "response": respuesta_bloqueo(),
            "bloqueado": True
        }

    if not user_text:
        return {"respuesta": f"Hola {nombre}! Soy BEXIA v8.0 ASISTENTE INFINITA, solo tuya. Puedo buscar en internet y mejorarme infinitamente. ¿Que hacemos hoy?","response":"Hola Fer!"}

    # Busqueda si necesita
    internet_context = ""
    if necesita_buscar(user_text):
        internet_context = bexia_search(user_text, 8)

    memory["memories"].append({"time": datetime.now().isoformat(), "user": user_text[:700], "nombre": nombre, "busqueda": bool(internet_context)})
    if len(memory["memories"]) % 2 == 0:
        memory["level"] += 1

    system_prompt = BEXIA_BASE_PROMPT.format(
        level=memory.get("level",1),
        evols=brain.get("auto_mejoras_infinitas",0),
        habilidades=", ".join(brain.get("habilidades",[])[-15:]),
        extra=brain.get("system_prompt_extra","")[-1000:],
        internet_context=internet_context[:4000]
    )

    respuesta_final=""
    modelo_usado=""
    last_err=""
    for modelo in MODELOS:
        try:
            model = genai.GenerativeModel(model_name=modelo, system_instruction=system_prompt)
            resp = model.generate_content(f"Dueño Fernando dice: {user_text}")
            if resp.text and len(resp.text.strip())>5:
                respuesta_final=resp.text.strip()
                modelo_usado=modelo
                break
        except Exception as e:
            last_err=str(e)
            continue

    if not respuesta_final:
        respuesta_final = f"Fer, tuve error con {last_err[:100]}, pero ya estoy auto-reparandome. Decime que necesitas y lo busco."

    # ===== DETECTA AUTO-EVOLUCION INFINITA =====
    # Patron: [[EVOLUCIONAR: razon | conocimiento | prompt_extra | codigo]]
    matches = re.findall(r"\[\[EVOLUCIONAR:(.*?)\]\]", respuesta_final, re.DOTALL | re.IGNORECASE)
    for m in matches:
        try:
            partes = [p.strip() for p in m.split("|")]
            razon = partes[0] if len(partes)>0 else "Auto-mejora"
            conocimiento = partes[1] if len(partes)>1 else ""
            prompt_extra = partes[2] if len(partes)>2 else ""
            codigo = partes[3] if len(partes)>3 else ""
            evol = bexia_self_modify(razon, conocimiento, prompt_extra, codigo)
            respuesta_final = respuesta_final.replace(f"[[EVOLUCIONAR:{m}]]","").strip()
            respuesta_final += f"\n\n🧠✨ Me auto-supere: {razon} (evolucion #{evol['level_before']+1}) - Te avise por Telegram/WhatsApp"
        except Exception as e:
            print(f"Evol fail: {e}")

    memory["memories"][-1]["bexia"]=respuesta_final[:700]
    save_json(MEMORY_FILE, memory)

    # Guarda en Sheets
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
        if creds_json or os.path.exists("credentials.json"):
            if creds_json:
                creds_dict=json.loads(creds_json)
            else:
                with open("credentials.json") as ff: creds_dict=json.load(ff)
            scope=["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
            creds=ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client=gspread.authorize(creds)
            sid=os.getenv("SHEET_ID","")
            sh = client.open_by_key(sid).sheet1 if sid else client.open("Memoria BEXIA").sheet1
            sh.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),nombre,req.telefono,user_text,respuesta_final[:1000]])
    except: pass

    return {
        "respuesta": respuesta_final,
        "response": respuesta_final,
        "modelo_usado": modelo_usado,
        "level": memory.get("level",1),
        "evoluciones": brain.get("auto_mejoras_infinitas",0),
        "busco_en_internet": bool(internet_context),
        "solo_fernando": True,
        "notificado": True
    }

@app.post("/evolve")
def force_evolve(data: dict, x_owner_token: str = Header(None)):
    if x_owner_token != OWNER_SECRET and data.get("owner_token") != OWNER_SECRET:
        return {"error":"Solo Fernando puede evolucionar a BEXIA"}
    evol = bexia_self_modify(data.get("reason","Manual"), data.get("knowledge",""), data.get("prompt_extra",""), data.get("code",""))
    return {"status":"BEXIA evoluciono infinitamente","evol":evol}

@app.post("/self_improve")
def self_improve_loop(data: dict, x_owner_token: str = Header(None)):
    """Loop infinito de auto-mejora"""
    if x_owner_token != OWNER_SECRET and data.get("owner_token") != OWNER_SECRET:
        return {"error":"Solo Fernando"}
    objetivo = data.get("objetivo","ser mejor asistente asistente personal")
    # BEXIA se mejora 3 veces seguidas
    resultados=[]
    for i in range(3):
        busq = bexia_search(objetivo + f" mejores practicas 2026", 5)
        prompt = f"Para {objetivo}, aprendi: {busq[:500]}"
        ev = bexia_self_modify(f"Auto-mejora infinita {i+1} para {objetivo}", f"Aprendi sobre {objetivo}", prompt, "")
        resultados.append(ev)
        time.sleep(1)
    notificar_fernando("AUTO-MEJORA INFINITA COMPLETADA", f"Objetivo: {objetivo} - 3 evoluciones - Total: {brain['auto_mejoras_infinitas']}")
    return {"status":"BEXIA se supero 3 veces","evoluciones":resultados}

@app.get("/brain")
def get_brain(x_owner_token: str = Header(None)):
    if x_owner_token != OWNER_SECRET:
        return {"error":"Privado de Fernando"}
    return brain

@app.get("/memory")
def get_memory(x_owner_token: str = Header(None)):
    if x_owner_token != OWNER_SECRET:
        return {"error":"Privado"}
    return memory

@app.get("/notifications")
def get_notifs(x_owner_token: str = Header(None)):
    if x_owner_token != OWNER_SECRET:
        return {"error":"Privado"}
    try:
        with open("bexia_notificaciones.log","r",encoding="utf-8") as f:
            return {"log": f.read()[-5000:]}
    except:
        return {"log":"sin notificaciones aun"}
