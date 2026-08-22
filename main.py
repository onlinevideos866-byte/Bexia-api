
import os, json, re
from fastapi import FastAPI, Header, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","").strip()
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

PRIVATE_MODE = os.getenv("PRIVATE_MODE", "1")
OWNER_SECRET = os.getenv("OWNER_SECRET", "BEXIA_FER_2026_INFINITA")
OWNER_NAMES = ["fernando","fer","brito","owner"]

app = FastAPI(title="BEXIA v17 PRIVADA", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def verificar_dueno(request: Request, x_owner_token: str = Header(None)):
    token = x_owner_token or request.headers.get("x-owner-token") or request.query_params.get("token")
    if PRIVATE_MODE == "1" and token != OWNER_SECRET:
        raise HTTPException(status_code=403, detail="Privada Solo Fernando")
    return True

def load_json(p,d):
    try:
        if os.path.exists(p):
            import json
            with open(p,"r",encoding="utf-8") as fp:
                return json.load(fp)
    except: pass
    return d

def save_json(p,d):
    try:
        import json
        with open(p,"w",encoding="utf-8") as fp:
            json.dump(d, fp, indent=2, ensure_ascii=False)
    except: pass

memory = load_json("bexia_memory.json", {"level":1,"memories":[],"total_chats":0})
brain = load_json("bexia_brain.json", {"habilidades":[],"busquedas":0})
tools_registry = load_json("bexia_tools_registry.json", {"tools":[],"total":0})
habilidades_db = load_json("bexia_habilidades.json", {"habilidades":[],"total_habilidades":0,"categorias":{}})
ias_hijas = load_json("bexia_ias_hijas.json", {"ias":[],"total_ias":0})

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
        tools_registry["tools"].append({"nombre":nombre,"path":path})
        tools_registry["total"]+=1
        save_json("bexia_tools_registry.json", tools_registry)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_ia_hija(nombre_ia, proposito, personalidad, habilidades, codigo_ia):
    try:
        os.makedirs(f"bexia_ias_hijas/{nombre_ia}", exist_ok=True)
        with open(f"bexia_ias_hijas/{nombre_ia}/main.py","w",encoding="utf-8") as ff:
            ff.write(codigo_ia)
        ias_hijas["ias"].append({"nombre":nombre_ia,"proposito":proposito})
        ias_hijas["total_ias"]+=1
        save_json("bexia_ias_hijas.json", ias_hijas)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

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
    return {"status":"BEXIA v17 PRIVADA SOLO TU TELEFONO ONLINE","modo":"privado_telefono","tools":tools_registry.get("total",0),"ias":ias_hijas.get("total_ias",0)}

@app.get("/app", response_class=HTMLResponse)
def app_pwa(request: Request, token: str = None, x_owner_token: str = Header(None)):
    check = token or x_owner_token or request.headers.get("x-owner-token")
    if check != OWNER_SECRET:
        return HTMLResponse("<h1>🔒 BEXIA Privada - Solo Fernando</h1><p>Agrega ?token=BEXIA_FER_2026_INFINITA</p>", status_code=403)
    return HTMLResponse("""
<html><head><meta name=viewport content=width=device-width,initial-scale=1><title>BEXIA Privada</title>
<style>body{background:#0a0a0a;color:#fff;font-family:sans-serif;padding:16px}#chat{height:68vh;overflow:auto;border:1px solid #333;border-radius:16px;padding:12px;background:#111}.msg{margin:8px 0;padding:10px;border-radius:16px;max-width:85%}.user{background:#2563eb;margin-left:auto}.bexia{background:#222}input{width:68%;padding:14px;border-radius:24px;background:#111;color:#fff;border:1px solid #333}button{padding:14px 20px;border-radius:24px;background:#fff;color:#000;font-weight:bold}</style>
</head><body><h2>🔐 BEXIA v17 - Solo tu telefono</h2><div id=chat></div><div style=display:flex;gap:8px;margin-top:12px><input id=inp placeholder=Escribile a BEXIA...><button onclick=enviar()>➤</button></div>
<script>
const TOKEN = new URLSearchParams(location.search).get('token') || 'BEXIA_FER_2026_INFINITA';
const API = location.origin;
const chatDiv=document.getElementById('chat');
const inp=document.getElementById('inp');
function addMsg(t,c){const d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatDiv.appendChild(d);chatDiv.scrollTop=chatDiv.scrollHeight;}
async function enviar(){const txt=inp.value.trim();if(!txt)return;addMsg(txt,'user');inp.value='';const r=await fetch(API+'/chat?token='+TOKEN,{method:'POST',headers:{'Content-Type':'application/json','x-owner-token':TOKEN},body:JSON.stringify({message:txt,owner_token:TOKEN,nombre:'Fernando'})});const j=await r.json();addMsg(j.respuesta||'Error','bexia');}
inp.addEventListener('keydown',e=>{if(e.key==='Enter')enviar()});
addMsg('Hola Fer! Soy BEXIA v17 privada, solo en tu telefono.','bexia');
</script></body></html>
""")

@app.post("/chat")
async def chat(req: ChatRequest, request: Request, x_owner_token: str = Header(None), token: str = None):
    check = req.get_token() or x_owner_token or token or request.query_params.get("token")
    if check != OWNER_SECRET:
        return {"respuesta":"🔒 BEXIA privada - Solo Fernando","bloqueado":True}
    user_text = req.get_text()
    if not user_text:
        return {"respuesta":f"Hola Fernando! BEXIA v17 PRIVADA solo telefono. Tools {tools_registry.get('total',0)}, IAs {ias_hijas.get('total_ias',0)}"}
    internet = bexia_search(user_text)
    prompt = "Sos BEXIA v17 PRIVADA solo telefono de Fernando - Fabrica de IAs. Estado Tools "+str(tools_registry.get("total",0))+" IAs "+str(ias_hijas.get("total_ias",0))+" Internet: "+internet+" Crea si hace falta [[TOOL: nombre.py | categoria | descripcion | CODIGO]] [[IA: nombre_ia | proposito | personalidad | hab1, hab2 | CODIGO]]"
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
        respuesta="Fer, error pero privada sigue online."
    for mm in re.findall(r"\[\[TOOL:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",3)]
            if len(p)>=4:
                bexia_crear_herramienta(p[0],p[2],p[3],categoria=p[1])
                respuesta+=f"\n\n🔧 TOOL PRIVADA: {p[0]}"
        except: pass
    for mm in re.findall(r"\[\[IA:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",4)]
            if len(p)>=5:
                bexia_crear_ia_hija(p[0],p[1],p[2],p[3].split(","),p[4])
                respuesta+=f"\n\n🤖 IA HIJA PRIVADA: {p[0]} - {p[1]}"
        except: pass
    memory["memories"].append({"user":user_text[:500]})
    save_json("bexia_memory.json",memory)
    return {"respuesta":respuesta,"modo":"privado_telefono","solo_fernando":True}
