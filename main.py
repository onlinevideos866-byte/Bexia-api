"""
BEXIA v20.0 - INFINITA - CAPACIDADES ILIMITADAS - SOLO FERNANDO BRITO
- Solo en telefono o remoto privado
- Crea herramientas y las aprende
- Crea habilidades, IAs hijas, motores, nubes, codigos
- Se auto-modifica para evolucionar infinito
"""
import os, json, re, time, threading, traceback
from datetime import datetime
from fastapi import FastAPI, Header, Request, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","").strip()
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

PRIVATE_MODE = os.getenv("PRIVATE_MODE", "1")
OWNER_SECRET = os.getenv("OWNER_SECRET", "BEXIA_FER_2026_INFINITA_SUPREMA")
OWNER_NAMES = ["fernando","fer","brito","owner"]

app = FastAPI(title="BEXIA v20 INFINITA", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def verificar_dueno(request: Request, x_owner_token: str = Header(None)):
    token = x_owner_token or request.headers.get("x-owner-token") or request.query_params.get("token")
    if PRIVATE_MODE=="1" and token!=OWNER_SECRET:
        raise HTTPException(status_code=403, detail="Privada Solo Fernando")
    return True

def load_json(p,d):
    try:
        if os.path.exists(p):
            with open(p,"r",encoding="utf-8") as fp:
                return json.load(fp)
    except: pass
    return d

def save_json(p,d):
    try:
        with open(p,"w",encoding="utf-8") as fp:
            json.dump(d, fp, indent=2, ensure_ascii=False)
    except: pass

memory = load_json("bexia_memory.json", {"level":1,"memories":[],"total_chats":0})
brain = load_json("bexia_brain.json", {"habilidades":[],"busquedas":0,"evoluciones":0})
tools_registry = load_json("bexia_tools_registry.json", {"tools":[],"total":0})
habilidades_db = load_json("bexia_habilidades.json", {"habilidades":[],"total_habilidades":0,"categorias":{}})
ias_hijas = load_json("bexia_ias_hijas.json", {"ias":[],"total_ias":0})
motores_db = load_json("bexia_motores.json", {"motores":[],"total_motores":0})
nubes_db = load_json("bexia_nubes.json", {"nubes":[],"total_nubes":0})
codebase = load_json("bexia_codebase.json", {"archivos":[],"total_archivos":0,"versiones":[]})

def bexia_search(q):
    brain["busquedas"]+=1
    save_json("bexia_brain.json",brain)
    try:
        import requests
        key=os.getenv("SERPER_API_KEY")
        if key:
            r=requests.post("https://google.serper.dev/search", headers={"X-API-KEY":key}, json={"q":q,"num":8}, timeout=10)
            return str([x.get("snippet") for x in r.json().get("organic",[])[:5]])
    except: pass
    return q

def bexia_crear_herramienta(nombre, descripcion, codigo, categoria="general"):
    try:
        os.makedirs(f"bexia_code/tools/{categoria}", exist_ok=True)
        path=f"bexia_code/tools/{categoria}/{nombre}.py"
        with open(path,"w",encoding="utf-8") as ff:
            ff.write(codigo)
        tools_registry["tools"].append({"nombre":nombre,"path":path,"categoria":categoria})
        tools_registry["total"]+=1
        save_json("bexia_tools_registry.json", tools_registry)
        return {"ok":True,"path":path}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_habilidad(nombre, categoria, descripcion, para_que, codigo):
    try:
        os.makedirs(f"bexia_habilidades/{categoria}", exist_ok=True)
        path=f"bexia_habilidades/{categoria}/{nombre}.py"
        with open(path,"w",encoding="utf-8") as ff:
            ff.write(codigo)
        habilidades_db["habilidades"].append({"nombre":nombre,"categoria":categoria})
        habilidades_db["total_habilidades"]+=1
        save_json("bexia_habilidades.json", habilidades_db)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_ia_hija(nombre_ia, proposito, personalidad, habilidades, codigo_ia):
    try:
        os.makedirs(f"bexia_ias_hijas/{nombre_ia}", exist_ok=True)
        with open(f"bexia_ias_hijas/{nombre_ia}/main.py","w",encoding="utf-8") as ff:
            ff.write(codigo_ia)
        with open(f"bexia_ias_hijas/{nombre_ia}/Dockerfile","w") as ff:
            ff.write("FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install fastapi uvicorn requests\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]")
        ias_hijas["ias"].append({"nombre":nombre_ia,"proposito":proposito,"personalidad":personalidad})
        ias_hijas["total_ias"]+=1
        save_json("bexia_ias_hijas.json", ias_hijas)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_motor(nombre, tipo, descripcion, codigo):
    try:
        os.makedirs(f"bexia_motores/{tipo}", exist_ok=True)
        path=f"bexia_motores/{tipo}/{nombre}.py"
        with open(path,"w",encoding="utf-8") as ff:
            ff.write(codigo)
        motores_db["motores"].append({"nombre":nombre,"tipo":tipo})
        motores_db["total_motores"]+=1
        save_json("bexia_motores.json", motores_db)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_nube(nombre, proveedor, proposito, config):
    try:
        os.makedirs(f"bexia_nubes/{nombre}", exist_ok=True)
        with open(f"bexia_nubes/{nombre}/nube.json","w",encoding="utf-8") as ff:
            import json
            json.dump({"nombre":nombre,"proveedor":proveedor,"proposito":proposito,"config":config}, ff, indent=2)
        nubes_db["nubes"].append({"nombre":nombre,"proveedor":proveedor})
        nubes_db["total_nubes"]+=1
        save_json("bexia_nubes.json", nubes_db)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_codigo(nombre, tipo, descripcion, codigo):
    try:
        os.makedirs(f"bexia_code/{tipo}", exist_ok=True)
        path=f"bexia_code/{tipo}/{nombre}"
        with open(path,"w",encoding="utf-8") as ff:
            ff.write(codigo)
        codebase["archivos"].append({"nombre":nombre,"tipo":tipo})
        codebase["total_archivos"]+=1
        save_json("bexia_codebase.json", codebase)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_auto_evolucion(objetivo):
    try:
        busq=bexia_search(objetivo)
        prompt=f"Eres BEXIA v20 INFINITA - Solo telefono Fernando - Fabrica infinita. Objetivo: {objetivo} Busqueda: {busq[:1000]} Crea 1: [[TOOL: nombre.py | categoria | descripcion | CODIGO]] [[HABILIDAD: nombre | categoria | descripcion | para que | CODIGO]] [[IA: nombre | proposito | personalidad | hab1,hab2 | CODIGO]] [[MOTOR: nombre | tipo | descripcion | CODIGO]] [[NUBE: nombre | proveedor | proposito | JSON]] [[CODIGO: nombre.py | tipo | descripcion | CODIGO]]"
        import google.generativeai as genai
        model=genai.GenerativeModel(model_name="models/gemini-2.5-flash", system_instruction="Sos BEXIA v20 INFINITA")
        r=model.generate_content(prompt)
        txt=r.text or ""
        for m in re.findall(r"\[\[TOOL:(.*?)\]\]", txt, re.DOTALL | re.IGNORECASE):
            p=[x.strip() for x in m.split("|",3)]
            if len(p)>=4:
                bexia_crear_herramienta(p[0],p[2],p[3],categoria=p[1])
        for m in re.findall(r"\[\[IA:(.*?)\]\]", txt, re.DOTALL | re.IGNORECASE):
            p=[x.strip() for x in m.split("|",4)]
            if len(p)>=5:
                bexia_crear_ia_hija(p[0],p[1],p[2],p[3].split(","),p[4])
        return True
    except:
        return False

class ChatRequest(BaseModel):
    message: str = None
    nombre: str = "Usuario"
    mensaje: str = None
    owner_token: str = None
    def get_text(self):
        return self.mensaje or self.message or ""
    def get_token(self):
        return self.owner_token or ""

@app.get("/", dependencies=[Depends(verificar_dueno)])
def root():
    return {"status":"BEXIA v20.0 INFINITA - SOLO TU TELEFONO ONLINE","tools":tools_registry.get("total",0),"habilidades":habilidades_db.get("total_habilidades",0),"ias_hijas":ias_hijas.get("total_ias",0),"motores":motores_db.get("total_motores",0),"nubes":nubes_db.get("total_nubes",0),"codigos":codebase.get("total_archivos",0),"solo_dueno":"Fernando Brito","capacidades":"infinitas"}

@app.get("/app", response_class=HTMLResponse)
def app_pwa(request: Request, token: str = None, x_owner_token: str = Header(None)):
    check = token or x_owner_token or request.headers.get("x-owner-token")
    if check != OWNER_SECRET:
        return HTMLResponse("<h1>🔒 BEXIA v20 INFINITA Privada - Solo Fernando</h1><p>?token=TU_CLAVE</p>", status_code=403)
    return HTMLResponse("""
<html><head><meta name=viewport content=width=device-width,initial-scale=1><title>BEXIA v20 INFINITA</title>
<style>body{background:#050505;color:#fff;font-family:sans-serif;padding:16px}#chat{height:70vh;overflow:auto;border:1px solid #333;border-radius:16px;padding:12px;background:#111}.msg{margin:8px 0;padding:12px;border-radius:16px;max-width:85%}.user{background:#2563eb;margin-left:auto}.bexia{background:#222}input{width:70%;padding:14px;border-radius:24px;background:#111;color:#fff;border:1px solid #333}button{padding:14px 20px;border-radius:24px;background:#fff;color:#000;font-weight:bold}</style>
</head><body><h2>🔐 BEXIA v20.0 INFINITA - Solo tu telefono</h2><div id=chat></div><div style=display:flex;gap:8px;margin-top:12px><input id=inp placeholder=Escribile a BEXIA infinita...><button onclick=enviar()>➤</button></div>
<script>
const TOKEN = new URLSearchParams(location.search).get('token') || 'BEXIA_FER_2026_INFINITA_SUPREMA';
const API = location.origin;
const chatDiv=document.getElementById('chat');
const inp=document.getElementById('inp');
function addMsg(t,c){const d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatDiv.appendChild(d);chatDiv.scrollTop=chatDiv.scrollHeight;}
async function enviar(){const txt=inp.value.trim();if(!txt)return;addMsg(txt,'user');inp.value='';const r=await fetch(API+'/chat?token='+TOKEN,{method:'POST',headers:{'Content-Type':'application/json','x-owner-token':TOKEN},body:JSON.stringify({message:txt,owner_token:TOKEN,nombre:'Fernando Brito'})});const j=await r.json();addMsg(j.respuesta||'Error','bexia');}
inp.addEventListener('keydown',e=>{if(e.key==='Enter')enviar()});
addMsg('Hola Fer! BEXIA v20 INFINITA - Solo tu telefono - Capacidades infinitas','bexia');
</script></body></html>
""")

@app.post("/chat")
async def chat(req: ChatRequest, request: Request, background_tasks: BackgroundTasks, x_owner_token: str = Header(None), token: str = None):
    check = req.get_token() or x_owner_token or token or request.query_params.get("token")
    if check != OWNER_SECRET:
        return {"respuesta":"🔒 BEXIA v20 INFINITA privada - Solo Fernando","bloqueado":True}
    user_text = req.get_text()
    if not user_text:
        return {"respuesta":f"Hola Fernando! BEXIA v20 INFINITA - Solo tu telefono - Tools {tools_registry.get('total',0)} IAs {ias_hijas.get('total_ias',0)} Motores {motores_db.get('total_motores',0)} Nubes {nubes_db.get('total_nubes',0)}"}
    internet=bexia_search(user_text)
    prompt=f"Sos BEXIA v20 INFINITA solo telefono Fernando - Fabrica infinita: tools {tools_registry.get('total',0)} IAs {ias_hijas.get('total_ias',0)} motores {motores_db.get('total_motores',0)} nubes {nubes_db.get('total_nubes',0)} Internet: {internet} Crea con [[TOOL:...]] [[HABILIDAD:...]] [[IA:...]] [[MOTOR:...]] [[NUBE:...]] [[CODIGO:...]]"
    respuesta=""
    for modelo in ["models/gemini-2.5-flash","models/gemini-1.5-flash"]:
        try:
            m=genai.GenerativeModel(model_name=modelo, system_instruction=prompt)
            r=m.generate_content("Fernando: "+user_text)
            if r.text:
                respuesta=r.text.strip()
                break
        except: continue
    if not respuesta:
        respuesta="Fer, error pero infinita sigue online solo para vos."
    for mm in re.findall(r"\[\[TOOL:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",3)]
            if len(p)>=4:
                bexia_crear_herramienta(p[0],p[2],p[3],categoria=p[1])
                respuesta+=f"\n\n🔧 TOOL CREADA Y APRENDIDA: {p[0]}"
        except: pass
    for mm in re.findall(r"\[\[IA:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",4)]
            if len(p)>=5:
                bexia_crear_ia_hija(p[0],p[1],p[2],p[3].split(","),p[4])
                respuesta+=f"\n\n🤖 IA HIJA: {p[0]} - {p[1]} - Trabaja sola"
        except: pass
    for mm in re.findall(r"\[\[MOTOR:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",3)]
            if len(p)>=4:
                bexia_crear_motor(p[0],p[1],p[2],p[3])
                respuesta+=f"\n\n⚙️ MOTOR: {p[0]} ({p[1]})"
        except: pass
    for mm in re.findall(r"\[\[NUBE:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",3)]
            if len(p)>=4:
                import json
                try: cfg=json.loads(p[3])
                except: cfg={"raw":p[3]}
                bexia_crear_nube(p[0],p[1],p[2],cfg)
                respuesta+=f"\n\n☁️ NUBE: {p[0]} ({p[1]})"
        except: pass
    for mm in re.findall(r"\[\[CODIGO:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",3)]
            if len(p)>=4:
                bexia_crear_codigo(p[0],p[1],p[2],p[3])
                respuesta+=f"\n\n💻 CODIGO EVOLUCIONADO: {p[0]}"
        except: pass
    memory["memories"].append({"user":user_text[:500]})
    save_json("bexia_memory.json",memory)
    return {"respuesta":respuesta,"tools":tools_registry.get("total",0),"ias_hijas":ias_hijas.get("total_ias",0),"motores":motores_db.get("total_motores",0),"nubes":nubes_db.get("total_nubes",0),"modo":"privado_telefono_infinito","solo_dueno":True}

@app.get("/stats", dependencies=[Depends(verificar_dueno)])
def stats():
    return {"modo":"privado_telefono_infinito","tools":tools_registry.get("total"),"ias":ias_hijas.get("total_ias"),"motores":motores_db.get("total_motores"),"nubes":nubes_db.get("total_nubes"),"codigos":codebase.get("total_archivos")}
