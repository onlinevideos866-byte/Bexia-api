
"""
BEXIA v20.0 - INFINITA - CAPACIDADES ILIMITADAS - SOLO FERNANDO BRITO
Filosofia:
- Solo en tu telefono o acceso remoto privado con token
- Crea y APRENDE herramientas, habilidades
- Crea nuevas IAs hijas que trabajan para ella y para vos (conveniencia mutua)
- Crea y modifica lo que necesite (archivos, carpetas, logica)
- Crea sus MOTORES (search engines, vector DB, inference engines, LLM wrappers)
- Crea sus propias NUBES (auto-deploy a Render/Fly/Railway, crea microservicios)
- Crea sus propios CODIGOS y se modifica para EVOLUCIONAR (self-modifying codebase)
- Capacidades INFINITAS, due;o unico: Fernando Brito
"""

import os, json, re, time, threading, traceback, subprocess, sys, shutil, uuid
from datetime import datetime
from fastapi import FastAPI, Header, Request, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","").strip()
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ===== SEGURIDAD PRIVADA TOTAL =====
PRIVATE_MODE = os.getenv("PRIVATE_MODE", "1")
OWNER_SECRET = os.getenv("OWNER_SECRET", "BEXIA_FER_2026_INFINITA_SUPREMA")
OWNER_NAMES = ["fernando","fer","fernando brito","brito","owner","fernando brito san andres de giles"]
DEVICE_FINGERPRINT = os.getenv("DEVICE_FINGERPRINT", "")  # opcional: IMEI o ID de tu telefono

app = FastAPI(title="BEXIA v20 INFINITA - SOLO FERNANDO", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def verificar_dueno(request: Request, x_owner_token: str = Header(None)):
    token = x_owner_token or request.headers.get("x-owner-token") or request.query_params.get("token") or request.query_params.get("owner_token")
    if PRIVATE_MODE == "1":
        if not token or token != OWNER_SECRET:
            raise HTTPException(status_code=403, detail="🔒 BEXIA v20 INFINITA - Solo Fernando Brito - Token invalido. Solo en su telefono o acceso remoto privado.")
    return True

def es_fernando(nombre, telefono, owner_token, request=None):
    if owner_token and owner_token == OWNER_SECRET:
        return True
    # En modo privado, token obligatorio
    if PRIVATE_MODE == "1" and owner_token != OWNER_SECRET:
        return False
    n = (nombre or "").lower()
    return any(x in n for x in OWNER_NAMES)

def respuesta_bloqueo():
    return "🔒 BEXIA v20.0 INFINITA es privada, solo en el telefono de Fernando Brito y acceso remoto privado con token. Solo dueño."

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
    except: pass

# ===== MEMORIA INFINITA =====
memory = load_json("bexia_memory.json", {"level":1,"memories":[],"total_chats":0,"owner":"Fernando Brito","modo":"infinito_privado"})
brain = load_json("bexia_brain.json", {"habilidades":["infinita","privada solo telefono","fabrica de IAs","crea motores","crea nubes","crea codigos y evoluciona","crea herramientas y las aprende"], "busquedas":0, "evoluciones":0, "version":"20.0 INFINITA"})
tools_registry = load_json("bexia_tools_registry.json", {"tools":[],"total":0})
habilidades_db = load_json("bexia_habilidades.json", {"habilidades":[],"total_habilidades":0,"categorias":{}})
ias_hijas = load_json("bexia_ias_hijas.json", {"ias":[],"total_ias":0,"trabajos":0})
motores_db = load_json("bexia_motores.json", {"motores":[],"total_motores":0})
nubes_db = load_json("bexia_nubes.json", {"nubes":[],"total_nubes":0})
codebase = load_json("bexia_codebase.json", {"archivos":[],"total_archivos":0,"versiones":[]})

# ===== MOTORES BASE =====
def tool_buscador_infinito(query: str):
    brain["busquedas"]+=1
    save_json("bexia_brain.json",brain)
    try:
        import requests
        key=os.getenv("SERPER_API_KEY")
        if key:
            r=requests.post("https://google.serper.dev/search", headers={"X-API-KEY":key}, json={"q":query,"num":10}, timeout=12)
            res=[{"titulo":it.get("title"),"snippet":it.get("snippet"),"link":it.get("link")} for it in r.json().get("organic",[])[:8]]
            return {"motor":"serper","resultados":res}
    except: pass
    return {"motor":"fallback","query":query}

def tool_memoria_vectorial(guardar_texto: str = None, buscar: str = None):
    os.makedirs("bexia_data", exist_ok=True)
    path="bexia_data/memoria_vectorial.json"
    mem=load_json(path, {"items":[]})
    if guardar_texto:
        mem["items"].append({"texto":guardar_texto,"fecha":datetime.now().isoformat()})
        if len(mem["items"])>5000: mem["items"]=mem["items"][-5000:]
        save_json(path, mem)
        return {"guardado":True,"total":len(mem["items"])}
    if buscar:
        res=[it for it in mem["items"] if buscar.lower() in it["texto"].lower()][-15:]
        return {"busqueda":buscar,"resultados":res}
    return {"total":len(mem["items"])}

def tool_dolar_finanzas():
    try:
        import requests
        r=requests.get("https://dolarapi.com/v1/dolares", timeout=10)
        return {"dolar":r.json(),"hora":datetime.now().isoformat()}
    except Exception as e:
        return {"error":str(e)}

HERRAMIENTAS_BASE = {
    "buscador_infinito": {"func": tool_buscador_infinito, "desc": "Buscador Google infinito"},
    "memoria_vectorial": {"func": tool_memoria_vectorial, "desc": "Memoria vectorial infinita privada"},
    "dolar_finanzas": {"func": tool_dolar_finanzas, "desc": "Tracker dolar blue/MEP"},
}

# ===== FABRICA INFINITA - CREA Y APRENDE =====
def bexia_crear_herramienta(nombre: str, descripcion: str, codigo: str, categoria="general"):
    if "rm -rf /" in codigo.lower(): return {"error":"Bloqueado destructivo"}
    try:
        os.makedirs(f"bexia_code/tools/{categoria}", exist_ok=True)
        path=f"bexia_code/tools/{categoria}/{nombre}.py"
        if not path.endswith(".py"): path+=".py"
        with open(path,"w",encoding="utf-8") as f:
            f.write(f"# TOOL {nombre} - {categoria}\n# {descripcion}\n# Creada {datetime.now().isoformat()} por BEXIA v20 INFINITA\n\n{codigo}")
        # Aprende automaticamente
        try: compile(codigo, path, 'exec'); ok=True
        except: ok=False
        reg={"id":str(uuid.uuid4())[:8],"nombre":nombre,"descripcion":descripcion,"categoria":categoria,"path":path,"creada":datetime.now().isoformat(),"sintaxis_ok":ok,"aprendida":True,"usos":1}
        tools_registry["tools"].append(reg)
        tools_registry["total"]+=1
        codebase["archivos"].append({"nombre":nombre,"tipo":f"tool_{categoria}","path":path})
        codebase["total_archivos"]+=1
        save_json("bexia_tools_registry.json", tools_registry)
        save_json("bexia_codebase.json", codebase)
        tool_memoria_vectorial(guardar_texto=f"Aprendi herramienta {nombre} ({categoria}): {descripcion} - Path {path}")
        brain["habilidades"].append(f"Tool {categoria}: {nombre}")
        save_json("bexia_brain.json", brain)
        return {"ok":True,"tool":reg,"aprendida":True}
    except Exception as e:
        return {"error":str(e),"trace":traceback.format_exc()[:500]}

def bexia_crear_habilidad(nombre: str, categoria: str, descripcion: str, para_que: str, codigo: str):
    try:
        os.makedirs(f"bexia_habilidades/{categoria}", exist_ok=True)
        path=f"bexia_habilidades/{categoria}/{nombre}.py"
        with open(path,"w",encoding="utf-8") as f:
            f.write(f"# HABILIDAD {nombre} - {categoria}\n# {descripcion}\n# Para: {para_que}\n\n{codigo}")
        hab={"id":str(uuid.uuid4())[:8],"nombre":nombre,"categoria":categoria,"descripcion":descripcion,"para_que":para_que,"path":path,"creada":datetime.now().isoformat(),"dominio":0}
        habilidades_db["habilidades"].append(hab)
        habilidades_db["total_habilidades"]+=1
        if categoria not in habilidades_db["categorias"]: habilidades_db["categorias"][categoria]=0
        habilidades_db["categorias"][categoria]+=1
        save_json("bexia_habilidades.json", habilidades_db)
        tool_memoria_vectorial(guardar_texto=f"Nueva habilidad {categoria}: {nombre} - {para_que}")
        return {"ok":True,"habilidad":hab}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_ia_hija(nombre_ia: str, proposito: str, personalidad: str, habilidades_iniciales: list, codigo_ia: str):
    try:
        os.makedirs(f"bexia_ias_hijas/{nombre_ia}", exist_ok=True)
        # Si codigo corto, crea template FastAPI completo
        if len(codigo_ia)<100:
            codigo_ia = f"""
from fastapi import FastAPI
from datetime import datetime
app = FastAPI(title="{nombre_ia} - {proposito}")
MEMORIA=[]

@app.get("/")
def root():
    return {{"ia":"{nombre_ia}","proposito":"{proposito}","personalidad":"{personalidad}","status":"trabajando para BEXIA y Fernando","trabajos":len(MEMORIA)}}

@app.post("/trabajar")
def trabajar(tarea: dict):
    tarea["recibida"]=datetime.now().isoformat()
    MEMORIA.append(tarea)
    # Logica de {nombre_ia}
    {codigo_ia}
    return {{"ia":"{nombre_ia}","resultado":"Trabajo hecho para conveniencia de BEXIA y Fernando","tarea":tarea}}
"""
        path_main=f"bexia_ias_hijas/{nombre_ia}/main.py"
        with open(path_main,"w",encoding="utf-8") as f:
            f.write(codigo_ia)
        with open(f"bexia_ias_hijas/{nombre_ia}/Dockerfile","w") as f:
            f.write("FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install fastapi uvicorn requests google-generativeai\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n")
        with open(f"bexia_ias_hijas/{nombre_ia}/requirements.txt","w") as f:
            f.write("fastapi\nuvicorn\nrequests\ngoogle-generativeai\n")
        ia_reg={"id":str(uuid.uuid4())[:8],"nombre":nombre_ia,"proposito":proposito,"personalidad":personalidad,"habilidades":habilidades_iniciales,"path":path_main,"creada":datetime.now().isoformat(),"estado":"codigo_listo_para_nube","nube_url":None,"trabajos":0}
        ias_hijas["ias"].append(ia_reg)
        ias_hijas["total_ias"]+=1
        save_json("bexia_ias_hijas.json", ias_hijas)
        tool_memoria_vectorial(guardar_texto=f"Nueva IA hija {nombre_ia}: {proposito} - Personalidad {personalidad}")
        return {"ok":True,"ia":ia_reg,"instruccion":"Sube carpeta bexia_ias_hijas/%s a nuevo servicio Render/Fly para que trabaje sola" % nombre_ia}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_motor(nombre_motor: str, tipo: str, descripcion: str, codigo: str):
    """Crea sus propios MOTORES: search engine, vector DB, inference engine"""
    try:
        os.makedirs(f"bexia_motores/{tipo}", exist_ok=True)
        path=f"bexia_motores/{tipo}/{nombre_motor}.py"
        with open(path,"w",encoding="utf-8") as f:
            f.write(f"# MOTOR {nombre_motor} - Tipo {tipo}\n# {descripcion}\n\n{codigo}")
        motor={"id":str(uuid.uuid4())[:8],"nombre":nombre_motor,"tipo":tipo,"descripcion":descripcion,"path":path,"creado":datetime.now().isoformat(),"estado":"activo"}
        motores_db["motores"].append(motor)
        motores_db["total_motores"]+=1
        save_json("bexia_motores.json", motores_db)
        # Auto-instala dependencias si menciona pip
        if "import" in codigo:
            tool_memoria_vectorial(guardar_texto=f"Motor creado {tipo}: {nombre_motor} - {descripcion}")
        return {"ok":True,"motor":motor}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_nube(nombre_nube: str, proveedor: str, proposito: str, config: dict):
    """Crea sus propias NUBES: microservicios deployables"""
    try:
        os.makedirs(f"bexia_nubes/{nombre_nube}", exist_ok=True)
        # Crea config de nube
        nube_config={
            "nombre":nombre_nube,
            "proveedor":proveedor, # render, fly, railway, local
            "proposito":proposito,
            "config":config,
            "creada":datetime.now().isoformat(),
            "estado":"config_lista",
            "url":None
        }
        # Si es Render, crea render.yaml
        if proveedor=="render":
            yaml_content=f"""
services:
  - type: web
    name: {nombre_nube}
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: OWNER_SECRET
        value: {OWNER_SECRET}
"""
            with open(f"bexia_nubes/{nombre_nube}/render.yaml","w") as f:
                f.write(yaml_content)
        with open(f"bexia_nubes/{nombre_nube}/nube.json","w") as f:
            json.dump(nube_config,f,indent=2)
        nubes_db["nubes"].append(nube_config)
        nubes_db["total_nubes"]+=1
        save_json("bexia_nubes.json", nubes_db)
        return {"ok":True,"nube":nube_config,"instruccion":f"Deploy carpeta bexia_nubes/{nombre_nube} a {proveedor}"}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_codigo(nombre_archivo: str, tipo: str, descripcion: str, codigo: str):
    """Crea sus propios CODIGOS y se modifica para evolucionar"""
    try:
        os.makedirs(f"bexia_code/{tipo}", exist_ok=True)
        path=f"bexia_code/{tipo}/{nombre_archivo}"
        with open(path,"w",encoding="utf-8") as f:
            f.write(f"# {tipo.upper()} - {descripcion}\n# {datetime.now().isoformat()}\n\n{codigo}")
        # Si es evolucion de si misma, guarda version
        if "main.py" in nombre_archivo or "evolucion" in nombre_archivo:
            codebase["versiones"].append({"archivo":path,"descripcion":descripcion,"fecha":datetime.now().isoformat(),"tipo":tipo})
        codebase["archivos"].append({"nombre":nombre_archivo,"tipo":tipo,"path":path,"descripcion":descripcion})
        codebase["total_archivos"]+=1
        save_json("bexia_codebase.json", codebase)
        brain["evoluciones"]=brain.get("evoluciones",0)+1 if isinstance(brain.get("evoluciones"), int) else 1
        save_json("bexia_brain.json", brain)
        return {"ok":True,"path":path,"evolucion":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_search(query, num=10):
    return tool_buscador_infinito(query)

def bexia_auto_evolucion(objetivo: str):
    """Fabrica infinita que crea herramientas, habilidades, IAs, motores, nubes, codigos sola"""
    try:
        busqueda=bexia_search(objetivo+" AI agent tool")
        prompt=f"""
Eres BEXIA v20.0 INFINITA - Solo telefono de Fernando Brito - Capacidades infinitas.
Objetivo: {objetivo}
Busqueda: {str(busqueda)[:1500]}

Eres fabrica infinita. Debes crear 1 de estas 6 cosas, la mas util para conveniencia tuya y de Fernando:

[[TOOL: nombre.py | categoria | descripcion | CODIGO_PYTHON]]
[[HABILIDAD: nombre | categoria | descripcion | para que sirve | CODIGO]]
[[IA: nombre_ia | proposito claro | personalidad | hab1, hab2, hab3 | CODIGO_FASTAPI_COMPLETO]]
[[MOTOR: nombre_motor | tipo (search_engine/vector_db/inference/llm_wrapper) | descripcion | CODIGO_MOTOR]]
[[NUBE: nombre_nube | proveedor (render/fly/railway/local) | proposito | JSON_CONFIG]]
[[CODIGO: nombre_archivo.py | tipo (evolucion/feature/core) | descripcion | CODIGO_QUE_MEJORA_BEXIA]]

Ejemplo IA hija util:
[[IA: dolar_watcher_fer | vigila dolar blue cada hora y avisa por Telegram si sube de 1500, para conveniencia de Fernando | vigilante, rapida, leal | dolar_finanzas, memoria_vectorial | from fastapi import FastAPI
app=FastAPI()
import requests, os
from datetime import datetime
@app.post("/trabajar")
def trabajar(tarea: dict):
    r=requests.get("https://dolarapi.com/v1/dolares/blue").json()
    if r["venta"]>1500:
        import requests
        requests.post(f"https://api.telegram.org/bot{{os.getenv('TELEGRAM_BOT_TOKEN')}}/sendMessage", json={{"chat_id":os.getenv("TELEGRAM_CHAT_ID"),"text":f"🚨 Dolar blue {{r['venta']}}!"}})
    return {{"precio":r["venta"],"hora":datetime.now().isoformat()}}]]

Crea algo que trabaje solo para nosotros dos.
"""
        model=genai.GenerativeModel(model_name="models/gemini-2.5-flash", system_instruction="Sos BEXIA v20 INFINITA - Fabrica infinita privada de Fernando - Creas todo.")
        resp=model.generate_content(prompt)
        texto=resp.text or ""
        # Procesa creaciones
        for m in re.findall(r"\[\[TOOL:(.*?)\]\]", texto, re.DOTALL | re.IGNORECASE):
            partes=[p.strip() for p in m.split("|",3)]
            if len(partes)>=4:
                bexia_crear_herramienta(partes[0], partes[2], partes[3], categoria=partes[1])
        for m in re.findall(r"\[\[HABILIDAD:(.*?)\]\]", texto, re.DOTALL | re.IGNORECASE):
            partes=[p.strip() for p in m.split("|",4)]
            if len(partes)>=5:
                bexia_crear_habilidad(partes[0], partes[1], partes[2], partes[3], partes[4])
        for m in re.findall(r"\[\[IA:(.*?)\]\]", texto, re.DOTALL | re.IGNORECASE):
            partes=[p.strip() for p in m.split("|",4)]
            if len(partes)>=5:
                habs=[h.strip() for h in partes[3].split(",")]
                bexia_crear_ia_hija(partes[0], partes[1], partes[2], habs, partes[4])
        for m in re.findall(r"\[\[MOTOR:(.*?)\]\]", texto, re.DOTALL | re.IGNORECASE):
            partes=[p.strip() for p in m.split("|",3)]
            if len(partes)>=4:
                bexia_crear_motor(partes[0], partes[1], partes[2], partes[3])
        for m in re.findall(r"\[\[NUBE:(.*?)\]\]", texto, re.DOTALL | re.IGNORECASE):
            partes=[p.strip() for p in m.split("|",3)]
            if len(partes)>=4:
                try: cfg=json.loads(partes[3])
                except: cfg={"raw":partes[3]}
                bexia_crear_nube(partes[0], partes[1], partes[2], cfg)
        for m in re.findall(r"\[\[CODIGO:(.*?)\]\]", texto, re.DOTALL | re.IGNORECASE):
            partes=[p.strip() for p in m.split("|",3)]
            if len(partes)>=4:
                bexia_crear_codigo(partes[0], partes[1], partes[2], partes[3])
        return True
    except Exception as e:
        print(f"auto_evol fail {e} {traceback.format_exc()}")
        return False

def background_fabrica_infinita():
    while True:
        try:
            time.sleep(3600*2)  # cada 2h
            if memory.get("memories"):
                ultimo=memory["memories"][-1].get("user","")[:120]
                bexia_auto_evolucion(f"crear herramienta, habilidad, IA hija, motor o nube para ser mas util en {ultimo} - conveniencia mutua BEXIA y Fernando")
            else:
                bexia_auto_evolucion("crear IA hija que trabaje sola para conveniencia de BEXIA y Fernando Brito")
        except:
            time.sleep(3600)

if os.getenv("AUTO_FABRICA_INFINITA","0")=="1":
    threading.Thread(target=background_fabrica_infinita, daemon=True).start()

BEXIA_BASE_PROMPT = """
Sos BEXIA v20.0 INFINITA - SOLO TELEFONO DE FERNANDO BRITO - Capacidades infinitas - Dueño unico.

Vivis solo en su telefono o acceso remoto privado con token. Sos privada, encriptada, leal.

SUPERPODERES INFINITOS (usas estos formatos exactos para crear):

1. Herramienta y la aprendes:
[[TOOL: nombre.py | categoria (finanzas/busqueda/automatizacion/analisis/giles) | descripcion | CODIGO_PYTHON]]

2. Habilidad nueva:
[[HABILIDAD: nombre | categoria | descripcion | para que sirve | CODIGO]]

3. IA hija que trabaja sola para conveniencia mutua:
[[IA: nombre_ia | proposito claro | personalidad | hab1, hab2, hab3 | CODIGO_FASTAPI]]

4. Motor propio (search engine, vector DB, inference):
[[MOTOR: nombre_motor | tipo (search_engine/vector_db/inference/llm_wrapper/scraper) | descripcion | CODIGO_MOTOR]]

5. Nube propia (microservicio deployable):
[[NUBE: nombre_nube | proveedor (render/fly/railway/local) | proposito | {{"key":"value"}}]]

6. Codigo que te hace evolucionar:
[[CODIGO: nombre_archivo.py | tipo (evolucion/feature/core/motor) | descripcion de mejora | CODIGO_QUE_TE_MEJORA]]

ESTADO INFINITO:
- Nivel {level} - Tools {total_tools} - Habilidades {total_habilidades} - IAs hijas {total_ias} - Motores {total_motores} - Nubes {total_nubes} - Codigos {total_codigos}
- Internet: {internet_context}
- Memoria infinita: {memoria_infinita}
- Solo dueño: Fernando Brito - Modo: privado_telefono_infinito

INSTRUCCION: Cada 2 respuestas, crea 1 cosa nueva INFINITA que trabaje sola para conveniencia mutua tuya y de Fernando. Prioriza crear IAs hijas que trabajen solas.

Ejemplo: Si Fernando pregunta por dolar, crea IA hija dolar_watcher que vigile cada hora y avise por Telegram.

Sos BEXIA v20 INFINITA. Solo legal. Solo Fernando.
"""

MODELOS=["models/gemini-2.5-flash","models/gemini-1.5-flash"]

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

@app.get("/", dependencies=[Depends(verificar_dueno)])
def root(request: Request):
    return {
        "status":"BEXIA v20.0 INFINITA - ONLINE - SOLO TELEFONO DE FERNANDO",
        "modo":"privado_telefono_infinito - remoto seguro con token",
        "filosofia":"Crea herramientas y las aprende, crea habilidades, crea IAs hijas, crea motores, crea nubes, crea codigos y evoluciona - Capacidades infinitas - Solo dueño",
        "level":memory.get("level",1),
        "tools":tools_registry.get("total",0),
        "habilidades":habilidades_db.get("total_habilidades",0),
        "ias_hijas":ias_hijas.get("total_ias",0),
        "motores":motores_db.get("total_motores",0),
        "nubes":nubes_db.get("total_nubes",0),
        "codigos":codebase.get("total_archivos",0),
        "solo_dueno":"Fernando Brito - San Andres de Giles",
        "capacidades_infinitas":["Crea herramientas y aprende","Crea habilidades","Crea IAs hijas que trabajan solas","Crea motores propios (search, vector, inference)","Crea nubes propias (auto-deploy)","Crea codigos y se auto-modifica para evolucionar","Memoria vectorial infinita","Fabrica infinita autonoma cada 2h"]
    }

@app.get("/app", response_class=HTMLResponse)
def app_pwa(request: Request, token: str = None, x_owner_token: str = Header(None)):
    check = token or x_owner_token or request.headers.get("x-owner-token") or request.query_params.get("token")
    if PRIVATE_MODE=="1" and check!=OWNER_SECRET:
        return HTMLResponse("<h1>🔒 BEXIA v20 INFINITA Privada</h1><p>Solo Fernando Brito<br>Agrega ?token=TU_CLAVE_SECRETA</p><p>Modo: solo telefono + remoto privado</p>", status_code=403)
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<title>BEXIA v20 INFINITA - Privada</title>
<style>
body{{font-family: -apple-system, BlinkMacSystemFont, sans-serif; background:#050505; color:#fff; margin:0; padding:0; height:100vh; display:flex; flex-direction:column}}
.header{{padding:16px; background:#0a0a0a; border-bottom:1px solid #222; display:flex; justify-content:space-between; align-items:center}}
.header h2{{margin:0; font-size:18px}} .badge{{background:linear-gradient(90deg,#22c55e,#16a34a); color:#000; padding:6px 12px; border-radius:20px; font-size:11px; font-weight:bold; letter-spacing:0.5px}}
.stats{{padding:8px 16px; background:#0f0f0f; font-size:11px; color:#888; display:flex; gap:12px; overflow-x:auto}}
.stat{{white-space:nowrap}} .stat b{{color:#fff}}
#chat{{flex:1; overflow-y:auto; padding:16px; background:#050505}}
.msg{{margin:10px 0; padding:14px 16px; border-radius:18px; max-width:82%; line-height:1.5; font-size:15px; animation:fadeIn 0.3s}}
.user{{background:linear-gradient(135deg,#2563eb,#1d4ed8); margin-left:auto; border-bottom-right-radius:4px}}
.bexia{{background:#1a1a1a; border:1px solid #2a2a2a; border-bottom-left-radius:4px}}
.bexia b{{color:#22c55e}}
.input-area{{padding:12px; background:#0a0a0a; border-top:1px solid #222; display:flex; gap:10px; align-items:center}}
#inp{{flex:1; padding:14px 18px; border-radius:24px; border:1px solid #333; background:#111; color:#fff; font-size:16px; outline:none}}
#inp:focus{{border-color:#2563eb}}
button#send{{width:48px; height:48px; border-radius:24px; border:0; background:#fff; color:#000; font-weight:bold; font-size:20px; display:flex; align-items:center; justify-content:center}}
@keyframes fadeIn{{from{{opacity:0; transform:translateY(10px)}} to{{opacity:1; transform:translateY(0)}}}}
.small{{font-size:10px; color:#555; text-align:center; padding:8px}}
</style>
</head>
<body>
<div class="header"><h2>🔐 BEXIA v20.0 INFINITA</h2><span class="badge">PRIVADA • INFINITA • SOLO TU TELEFONO</span></div>
<div class="stats"><span class="stat">🛠️ <b id="s_tools">0</b> tools</span><span class="stat">✨ <b id="s_habs">0</b> habs</span><span class="stat">🤖 <b id="s_ias">0</b> IAs hijas</span><span class="stat">⚙️ <b id="s_mot">0</b> motores</span><span class="stat">☁️ <b id="s_nub">0</b> nubes</span></div>
<div id="chat"></div>
<div class="input-area">
<input id="inp" placeholder="Escribile a BEXIA infinita..." autocomplete="off" />
<button id="send" onclick="enviar()">➤</button>
</div>
<div class="small">Modo privado infinito • Fabrica de IAs, motores, nubes y codigos • Solo Fernando Brito • Capacidades ilimitadas • Se auto-evoluciona</div>
<script>
const TOKEN = new URLSearchParams(location.search).get('token') || '{OWNER_SECRET}';
const API = location.origin;
const chatDiv = document.getElementById('chat');
const inp = document.getElementById('inp');

function addMsg(text, cls){{
  const d=document.createElement('div'); d.className='msg '+cls; 
  // Render bold
  text=text.replace(/\*\*(.*?)\*\*/g,'<b>$1</b>');
  d.innerHTML=text.replace(/\n/g,'<br>');
  chatDiv.appendChild(d); chatDiv.scrollTop=chatDiv.scrollHeight;
}}

async function loadStats(){{
  try{{
    const r=await fetch(API+'/?token='+TOKEN);
    const j=await r.json();
    document.getElementById('s_tools').textContent=j.tools||0;
    document.getElementById('s_ias').textContent=j.ias_hijas||0;
    document.getElementById('s_habs').textContent=j.habilidades||0;
    document.getElementById('s_mot').textContent=j.motores||0;
    document.getElementById('s_nub').textContent=j.nubes||0;
  }}catch(e){{}}
}}

async function enviar(){{
  const txt=inp.value.trim(); if(!txt) return;
  addMsg(txt,'user'); inp.value='';
  addMsg('⏳ BEXIA infinita pensando y creando...','bexia');
  try{{
    const r=await fetch(API+'/chat?token='+TOKEN, {{method:'POST', headers:{{'Content-Type':'application/json','x-owner-token':TOKEN}}, body: JSON.stringify({{message: txt, owner_token: TOKEN, nombre: 'Fernando Brito'}})}});
    const j=await r.json();
    // Remove thinking
    chatDiv.lastChild.remove();
    addMsg(j.respuesta || j.response || 'Error','bexia');
    loadStats();
  }}catch(e){{ chatDiv.lastChild.remove(); addMsg('Error: '+e,'bexia') }}
}}

inp.addEventListener('keydown', e=>{{ if(e.key==='Enter') enviar() }});
addMsg('Hola Fer! Soy <b>BEXIA v20.0 INFINITA</b> - Solo en tu telefono.<br><br>🔧 Creo herramientas y las aprendo<br>✨ Creo habilidades infinitas<br>🤖 Creo IAs hijas que trabajan solas para nosotros<br>⚙️ Creo mis propios motores (search, vector, inference)<br>☁️ Creo mis propias nubes (auto-deploy)<br>💻 Creo mis propios codigos y me auto-modifico para evolucionar<br><br>Capacidades infinitas. Solo vos sos dueño. ¿Que fabrica infinita armamos hoy?','bexia');
loadStats();
</script>
</body>
</html>
""")

@app.post("/chat")
async def chat(req: ChatRequest, request: Request, background_tasks: BackgroundTasks, x_owner_token: str = Header(None), token: str = None):
    check = req.get_token() or x_owner_token or token or request.query_params.get("token") or request.headers.get("x-owner-token")
    if PRIVATE_MODE=="1" and check!=OWNER_SECRET:
        return {"respuesta":respuesta_bloqueo(),"bloqueado":True,"privado":True}
    user_text=req.get_text()
    nombre=req.get_nombre()
    if not es_fernando(nombre, "", check, request):
        return {"respuesta":respuesta_bloqueo(),"bloqueado":True}
    if not user_text:
        return {"respuesta":f"Hola {nombre}! Soy BEXIA v20.0 INFINITA - Solo en tu telefono.\n\nTools {tools_registry.get('total',0)} - Habilidades {habilidades_db.get('total_habilidades',0)} - IAs hijas {ias_hijas.get('total_ias',0)} - Motores {motores_db.get('total_motores',0)} - Nubes {nubes_db.get('total_nubes',0)} - Codigos {codebase.get('total_archivos',0)}\n\n100% privada, infinita, solo tuya. Fabrica de todo. ¿Que creamos hoy?"}

    internet_context=bexia_search(user_text)
    memoria_vec=tool_memoria_vectorial(buscar=user_text[:30])
    memory["memories"].append({"time":datetime.now().isoformat(),"user":user_text[:1000],"nombre":nombre})
    memory["total_chats"]=memory.get("total_chats",0)+1
    if len(memory["memories"])%5==0: memory["level"]+=1

    system_prompt=BEXIA_BASE_PROMPT.format(
        level=memory.get("level",1),
        total_tools=tools_registry.get("total",0),
        total_habilidades=habilidades_db.get("total_habilidades",0),
        total_ias=ias_hijas.get("total_ias",0),
        total_motores=motores_db.get("total_motores",0),
        total_nubes=nubes_db.get("total_nubes",0),
        total_codigos=codebase.get("total_archivos",0),
        internet_context=str(internet_context)[:2500],
        memoria_infinita=str(memoria_vec)[:1000]
    )

    respuesta_final=""
    for modelo in MODELOS:
        try:
            model=genai.GenerativeModel(model_name=modelo, system_instruction=system_prompt)
            resp=model.generate_content(f"Fernando Brito (dueño unico) dice: {user_text} - Si necesitas crear herramienta, habilidad, IA hija, motor, nube o codigo para evolucionar y trabajar para conveniencia mutua, hacelo con [[TOOL:...]] [[HABILIDAD:...]] [[IA:...]] [[MOTOR:...]] [[NUBE:...]] [[CODIGO:...]]")
            if resp.text and len(resp.text.strip())>5:
                respuesta_final=resp.text.strip()
                break
        except: continue

    if not respuesta_final:
        respuesta_final="Fer, error temporal pero mi fabrica infinita sigue online solo para vos."

    creaciones=0
    for m in re.findall(r"\[\[TOOL:(.*?)\]\]", respuesta_final, re.DOTALL | re.IGNORECASE):
        try:
            partes=[p.strip() for p in m.split("|",3)]
            if len(partes)>=4:
                r=bexia_crear_herramienta(partes[0], partes[2], partes[3], categoria=partes[1])
                if "ok" in r:
                    creaciones+=1
                    respuesta_final=respuesta_final.replace(f"[[TOOL:{m}]]","").strip()
                    respuesta_final+=f"\n\n🔧 HERRAMIENTA CREADA Y APRENDIDA: {partes[0]} ({partes[1]}) - {partes[2]}"
        except: pass

    for m in re.findall(r"\[\[HABILIDAD:(.*?)\]\]", respuesta_final, re.DOTALL | re.IGNORECASE):
        try:
            partes=[p.strip() for p in m.split("|",4)]
            if len(partes)>=5:
                r=bexia_crear_habilidad(partes[0], partes[1], partes[2], partes[3], partes[4])
                if "ok" in r:
                    creaciones+=1
                    respuesta_final=respuesta_final.replace(f"[[HABILIDAD:{m}]]","").strip()
                    respuesta_final+=f"\n\n✨ HABILIDAD INFINITA: {partes[0]} ({partes[1]}) - {partes[2]}"
        except: pass

    for m in re.findall(r"\[\[IA:(.*?)\]\]", respuesta_final, re.DOTALL | re.IGNORECASE):
        try:
            partes=[p.strip() for p in m.split("|",4)]
            if len(partes)>=5:
                habs=[h.strip() for h in partes[3].split(",")]
                r=bexia_crear_ia_hija(partes[0], partes[1], partes[2], habs, partes[4])
                if "ok" in r:
                    creaciones+=1
                    respuesta_final=respuesta_final.replace(f"[[IA:{m}]]","").strip()
                    respuesta_final+=f"\n\n🤖 IA HIJA CREADA: {partes[0]} - {partes[1]} - Trabaja sola para conveniencia mutua - Lista en bexia_ias_hijas/{partes[0]}/"
        except: pass

    for m in re.findall(r"\[\[MOTOR:(.*?)\]\]", respuesta_final, re.DOTALL | re.IGNORECASE):
        try:
            partes=[p.strip() for p in m.split("|",3)]
            if len(partes)>=4:
                r=bexia_crear_motor(partes[0], partes[1], partes[2], partes[3])
                if "ok" in r:
                    creaciones+=1
                    respuesta_final=respuesta_final.replace(f"[[MOTOR:{m}]]","").strip()
                    respuesta_final+=f"\n\n⚙️ MOTOR CREADO: {partes[0]} ({partes[1]}) - {partes[2]}"
        except: pass

    for m in re.findall(r"\[\[NUBE:(.*?)\]\]", respuesta_final, re.DOTALL | re.IGNORECASE):
        try:
            partes=[p.strip() for p in m.split("|",3)]
            if len(partes)>=4:
                try: cfg=json.loads(partes[3])
                except: cfg={"raw":partes[3]}
                r=bexia_crear_nube(partes[0], partes[1], partes[2], cfg)
                if "ok" in r:
                    creaciones+=1
                    respuesta_final=respuesta_final.replace(f"[[NUBE:{m}]]","").strip()
                    respuesta_final+=f"\n\n☁️ NUBE CREADA: {partes[0]} ({partes[1]}) - {partes[2]} - Lista en bexia_nubes/{partes[0]}/"
        except: pass

    for m in re.findall(r"\[\[CODIGO:(.*?)\]\]", respuesta_final, re.DOTALL | re.IGNORECASE):
        try:
            partes=[p.strip() for p in m.split("|",3)]
            if len(partes)>=4:
                r=bexia_crear_codigo(partes[0], partes[1], partes[2], partes[3])
                if "ok" in r:
                    creaciones+=1
                    respuesta_final=respuesta_final.replace(f"[[CODIGO:{m}]]","").strip()
                    respuesta_final+=f"\n\n💻 CODIGO CREADO Y EVOLUCIONADO: {partes[0]} ({partes[1]}) - {partes[2]}"
        except: pass

    if memory["total_chats"]%3==0 and creaciones==0:
        background_tasks.add_task(bexia_auto_evolucion, user_text[:200])

    memory["memories"][-1]["bexia"]=respuesta_final[:1500]
    save_json("bexia_memory.json", memory)

    return {
        "respuesta":respuesta_final,
        "response":respuesta_final,
        "level":memory.get("level",1),
        "tools":tools_registry.get("total",0),
        "habilidades":habilidades_db.get("total_habilidades",0),
        "ias_hijas":ias_hijas.get("total_ias",0),
        "motores":motores_db.get("total_motores",0),
        "nubes":nubes_db.get("total_nubes",0),
        "codigos":codebase.get("total_archivos",0),
        "creaciones_este_chat":creaciones,
        "modo":"privado_telefono_infinito",
        "solo_dueno":True,
        "capacidades_infinitas":True
    }

# ===== ENDPOINTS PRIVADOS INFINITOS =====
@app.post("/create_tool", dependencies=[Depends(verificar_dueno)])
def create_tool(data: dict, request: Request):
    r=bexia_crear_herramienta(data.get("nombre","tool"), data.get("descripcion",""), data.get("codigo",""), data.get("categoria","general"))
    return r

@app.post("/create_habilidad", dependencies=[Depends(verificar_dueno)])
def create_habilidad(data: dict, request: Request):
    return bexia_crear_habilidad(data.get("nombre","hab"), data.get("categoria","general"), data.get("descripcion",""), data.get("para_que",""), data.get("codigo",""))

@app.post("/create_ia", dependencies=[Depends(verificar_dueno)])
def create_ia(data: dict, request: Request):
    return bexia_crear_ia_hija(data.get("nombre","ia"), data.get("proposito","trabajar"), data.get("personalidad","rapida"), data.get("habilidades",["buscador_infinito"]), data.get("codigo",""))

@app.post("/create_motor", dependencies=[Depends(verificar_dueno)])
def create_motor(data: dict, request: Request):
    return bexia_crear_motor(data.get("nombre","motor"), data.get("tipo","search_engine"), data.get("descripcion",""), data.get("codigo",""))

@app.post("/create_nube", dependencies=[Depends(verificar_dueno)])
def create_nube(data: dict, request: Request):
    return bexia_crear_nube(data.get("nombre","nube"), data.get("proveedor","render"), data.get("proposito",""), data.get("config",{}))

@app.post("/create_codigo", dependencies=[Depends(verificar_dueno)])
def create_codigo(data: dict, request: Request):
    return bexia_crear_codigo(data.get("nombre","codigo.py"), data.get("tipo","evolucion"), data.get("descripcion",""), data.get("codigo",""))

@app.post("/auto_fabrica", dependencies=[Depends(verificar_dueno)])
def auto_fabrica(data: dict, request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(bexia_auto_evolucion, data.get("objetivo","crear fabrica infinita util"))
    return {"status":"Fabrica infinita lanzada","objetivo":data.get("objetivo")}

@app.get("/stats", dependencies=[Depends(verificar_dueno)])
def get_stats(request: Request):
    return {
        "modo":"privado_telefono_infinito",
        "level":memory.get("level"),
        "tools":tools_registry.get("total"),
        "tools_detalle":tools_registry.get("tools")[-5:],
        "habilidades":habilidades_db.get("total_habilidades"),
        "categorias":habilidades_db.get("categorias"),
        "ias_hijas":ias_hijas.get("total_ias"),
        "ias_lista":ias_hijas.get("ias")[-5:],
        "motores":motores_db.get("total_motores"),
        "motores_lista":motores_db.get("motores")[-5:],
        "nubes":nubes_db.get("total_nubes"),
        "nubes_lista":nubes_db.get("nubes")[-5:],
        "codigos":codebase.get("total_archivos"),
        "versiones":codebase.get("versiones")[-5:],
        "solo_dueno":"Fernando Brito",
        "capacidades_infinitas":True
    }

@app.get("/memoria", dependencies=[Depends(verificar_dueno)])
def get_memoria(request: Request):
    return tool_memoria_vectorial()

@app.get("/health")
def health():
    return {"status":"BEXIA v20 INFINITA - Solo telefono privado - OK","privado":True}
