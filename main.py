
import os, json, re, time, uuid, random
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

print("BEXIA v72 CONEXION DIRECTA - Directo a tu netbook - Iniciando...", flush=True)
VERSION="v72"
TOKEN="BEXIA_FER_2026_INFINITA_SUPREMA"
app=FastAPI(title="BEXIA v72 DIRECTA", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def load_json(p,d):
    try:
        if os.path.exists(p):
            with open(p,"r",encoding="utf-8") as f: return json.load(f)
    except: pass
    return d
def save_json(p,d):
    try:
        with open(p,"w",encoding="utf-8") as f: json.dump(f,d,indent=2,ensure_ascii=False)
    except: pass

sesiones_persist=load_json("bexia_sesiones.json", {})
herramientas=load_json("bexia_herramientas.json", {"cache":{},"versiones_codigo":[],"workflows_n8n":[],"conexiones_ia":[],"clones_creados":[],"herramientas_meta_ai":[],"aprendizajes":[],"tareas":[],"programas":[],"proyectos":[],"netbooks":[],"conexiones_directas":[]})
memoria_propia=load_json("bexia_memoria_propia.json", {"recuerdos":[],"auto_memorias":[],"aprendizajes":[],"modo_aprende":True,"ciclos":10,"estilo":"directo","netbook_conectada":True,"token":TOKEN})

try:
    if len(herramientas.get("programas",[])) == 0:
        tid="maestra_"+str(uuid.uuid4())[:6]
        hm={"id":tid,"tipo":"herramienta_maestra","nombre":"Herramienta Maestra Fer","objetivo":"Todo en uno - Conexion directa","codigo":"# Herramienta Maestra","lenguaje":"python","fecha":datetime.now().isoformat(),"lineas":10,"creado_por":"Bexia v72 Auto","estilo":"herramienta_maestra"}
        herramientas["programas"].append(hm)
        save_json("bexia_herramientas.json", herramientas)
except: pass

rate={}
sesiones_mem={}

def get_session(sid):
    if not sid: sid="publico"
    try: sid=re.sub(r"[^a-zA-Z0-9_-]","",sid)[:32] or "publico"
    except: sid="publico"
    if sid not in sesiones_mem: sesiones_mem[sid]=sesiones_persist.get(sid,[])[:50]
    return sid
def persist_session(sid):
    try:
        sesiones_persist[sid]=sesiones_mem.get(sid,[])[:50]
        save_json("bexia_sesiones.json", sesiones_persist)
    except: pass
def check_rate(ip):
    ahora=time.time()
    lst=rate.get(ip,[])
    lst=[t for t in lst if ahora-t<60]
    if len(lst)>=60: return False
    lst.append(ahora); rate[ip]=lst
    return True

def generar_programa(tipo, objetivo):
    cid=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    programa={"id":cid,"tipo":tipo,"nombre":objetivo[:50],"objetivo":objetivo[:200],"codigo":"# "+objetivo+" - ID "+cid,"lenguaje":"python","fecha":fecha,"lineas":10,"creado_por":"Bexia "+VERSION,"estilo":tipo}
    herramientas["programas"].append(programa)
    save_json("bexia_herramientas.json", herramientas)
    return programa

class ChatReq(BaseModel):
    message: str=""
    session_id: str="publico"

class DirectReq(BaseModel):
    token: str=""
    netbook_id: str=""

def cerebro(t):
    tl=t.lower().strip()
    if any(p in tl for p in ["conectar directamente","conectarte directamente","conexion directa","conecta directo","directo a bexia","conectar directo"]):
        prog=generar_programa("conexion_directa", "Conexion directa netbook a Bexia - Bypass Render")
        herramientas["conexiones_directas"].append({"id":prog["id"],"fecha":datetime.now().isoformat(),"tipo":"directa","token":TOKEN})
        save_json("bexia_herramientas.json", herramientas)
        return "CONEXION DIRECTA ACTIVADA v72\n\nLOCAL (mas rapida): http://localhost:7777/app?token="+TOKEN+"\nRED LOCAL (celu->netbook): http://TU_IP:7777/app?token="+TOKEN+"\nNUBE: https://bexia-api.onrender.com/app\n\nEn tu netbook deja abierta la ventana negra Uvicorn running on 0.0.0.0:7777 y abre Chrome en localhost:7777/app?token="+TOKEN+"\nPanel: /directo"
    if "mis programas" in tl or "programas"==tl:
        return "Programas: "+str(len(herramientas.get("programas",[])))+" - Conexion directa ON - Token: "+TOKEN[:10]+"... - Usa /directo"
    if tl in ["hola","buenas","test","meta"]:
        return "Hola Fer! Bexia "+VERSION+" CONEXION DIRECTA - Directo a tu netbook Bangho - Local: http://localhost:7777/app?token="+TOKEN+" - Nube: /meta - Deci 'conectarte directamente' - /directo panel"
    return "Recibi '"+t[:60]+"' - Bexia "+VERSION+" DIRECTA: 'conectarte directamente' -> conexion directa - Local: http://localhost:7777/app?token="+TOKEN

@app.get("/")
def root(): return {"bexia":VERSION+" CONEXION DIRECTA","token":TOKEN,"local":"http://localhost:7777/app?token="+TOKEN,"nube":"https://bexia-api.onrender.com","live":True}

@app.get("/health")
def health(): return {"status":"ok","bexia":VERSION,"token":TOKEN,"local_url":"http://localhost:7777/app?token="+TOKEN,"live":True}

@app.get("/directo", response_class=HTMLResponse)
def directo_page():
    html_content = """
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CONEXION DIRECTA - Bexia v72</title>
<style>
body{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:900px;margin:0 auto}
h1{background:linear-gradient(90deg,#0064e0,#22c55e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:20px}
.card{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #333}
.blue{border-color:#0064e0;background:rgba(0,100,224,.15)} .green{border-color:#22c55e;background:rgba(34,197,94,.15)} .yellow{border-color:#f59e0b;background:rgba(245,158,11,.15)}
pre{background:#000;padding:12px;border-radius:8px;overflow:auto;font-size:12px;white-space:pre-wrap;word-break:break-all}
button{background:#22c55e;color:#000;padding:12px 20px;border:none;border-radius:999px;font-weight:900;cursor:pointer;width:100%;margin:8px 0;font-size:14px}
a{color:#fff;padding:10px 14px;border-radius:999px;display:inline-block;margin:4px;text-decoration:none;font-weight:700;font-size:13px}
</style></head><body>
<h1>💻🔗 BEXIA v72 - CONEXION DIRECTA A TU NETBOOK</h1>
<div class="card blue"><b>🎯 ESTAS A 1 CLICK DE CONECTARTE DIRECTAMENTE</b><br>
Tu netbook Bangho ya tiene Bexia corriendo en <b>localhost:7777</b> con token <b>BEXIA_FER_2026_INFINITA_SUPREMA</b><br>
No necesitas Render, es instantaneo y sin internet.</div>

<div class="card green">
<h3>✅ OPCION 1: DIRECTA LOCAL (MAS RAPIDA)</h3>
<pre>http://localhost:7777/app?token=BEXIA_FER_2026_INFINITA_SUPREMA</pre>
<button onclick="window.open('http://localhost:7777/app?token=BEXIA_FER_2026_INFINITA_SUPREMA','_blank')">🚀 ABRIR CONEXION DIRECTA LOCALHOST:7777</button>
<p style="font-size:11px;color:#aaa">Si estas en tu netbook, este boton te conecta directo.</p>
</div>

<div class="card blue">
<h3>✅ OPCION 2: RED LOCAL (CELU -> NETBOOK, MISMA WIFI)</h3>
<p>1. En tu netbook CMD: ipconfig -> IPv4: ej 192.168.1.105<br>
2. En tu celu (misma WiFi): http://192.168.1.105:7777/app?token=BEXIA_FER_2026_INFINITA_SUPREMA</p>
<button onclick="let ip=prompt('Escribe tu IP (ej: 192.168.1.105):'); if(ip) window.open('http://'+ip+':7777/app?token=BEXIA_FER_2026_INFINITA_SUPREMA','_blank')">📱 CONECTAR CELU A NETBOOK</button>
</div>

<div class="card yellow">
<h3>☁️ OPCION 3: NUBE</h3>
<pre>https://bexia-api.onrender.com/app
https://bexia-api.onrender.com/meta
https://bexia-api.onrender.com/simple</pre>
<a href="/app" style="background:#7c3aed;color:#fff">/app Nube</a> <a href="/meta" style="background:#0064e0;color:#fff">/meta</a> <a href="/simple" style="background:#ff6a00;color:#fff">/simple</a>
</div>

<div class="card">
<h3>❓ No anda localhost:7777?</h3>
<p>1. Ventana negra Uvicorn running on 0.0.0.0:7777 debe estar abierta<br>
2. Si la cerraste, doble click a Bexia-Os-V37-Hermes.html en Descargas<br>
3. Espera Application startup complete</p>
</div>

<div class="card">
<a href="/conectar" style="background:#22c55e;color:#000">🔗 /conectar</a> <a href="/programador" style="background:#000;color:#fff;border:1px solid #333">💻 /programador</a>
</div>

</body></html>
"""
    return HTMLResponse(html_content)

@app.get("/conectar", response_class=HTMLResponse)
def conectar_page():
    return HTMLResponse("""
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>Conectar</title>
<style>body{background:#050510;color:#fff;font-family:system-ui;padding:16px} .card{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #333} a{color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px;text-decoration:none}</style></head><body>
<h1>💻🔗 Conectar Netbook</h1>
<div class="card" style="border-color:#22c55e"><b>DIRECTA:</b> http://localhost:7777/app?token=BEXIA_FER_2026_INFINITA_SUPREMA<br><a href="/directo" style="background:#22c55e;color:#000;font-weight:900">🔗 Ir a /directo</a></div>
</body></html>
""")

@app.get("/simple", response_class=HTMLResponse)
def simple():
    return HTMLResponse("""
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>Bexia v72 DIRECTA</title>
<style>body{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:600px;margin:0 auto} .card{background:#12122a;padding:14px;border-radius:16px;margin:10px 0;border:1px solid #333} input{width:100%;padding:14px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;box-sizing:border-box} button{width:100%;padding:14px;background:linear-gradient(90deg,#0064e0,#22c55e);border:none;border-radius:999px;color:#fff;font-weight:900;margin-top:8px} a{color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px;text-decoration:none}</style></head><body>
<h1>💻🔗 BEXIA v72 CONEXION DIRECTA</h1>
<div class="card" style="border-color:#22c55e"><b>DIRECTA:</b> http://localhost:7777/app?token=BEXIA_FER_2026_INFINITA_SUPREMA</div>
<div class="card"><form action="/chat_simple" method="get"><input type="text" name="message" placeholder="Ej: conectarte directamente" required><button type="submit">Conectar ></button></form></div>
<div class="card"><a href="/directo" style="background:#22c55e;color:#000;font-weight:900">🔗 /directo Panel directa</a> <a href="/simple" style="background:#ff6a00;color:#fff">/simple</a></div>
</body></html>
""")

@app.get("/chat_simple", response_class=HTMLResponse)
def chat_simple(message: str = "Hola"):
    r=cerebro(message)
    html_resp = "<html><head><meta charset='utf-8'><meta name=viewport content='width=device-width,initial-scale=1'><title>Bexia v72</title><style>body{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:700px;margin:0 auto} .card{background:#12122a;padding:14px;border-radius:16px;margin:12px 0;border:1px solid #333} pre{background:#000;padding:12px;border-radius:8px;white-space:pre-wrap;font-size:13px} input{width:100%;padding:14px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;box-sizing:border-box} button{width:100%;padding:14px;background:linear-gradient(90deg,#0064e0,#22c55e);border:none;border-radius:999px;color:#fff;font-weight:900;margin-top:8px}</style></head><body><h1>💻 BEXIA v72 DIRECTA</h1><div class='card'><b>Tu:</b> "+message[:500]+"</div><div class='card'><b>Bexia Directa:</b><pre>"+r[:6000]+"</pre></div><div class='card'><form action='/chat_simple' method='get'><input type='text' name='message' placeholder='otro mensaje' required><button type='submit'>Enviar otro ></button></form></div><div class='card'><a href='/directo' style='background:#22c55e;color:#000;padding:8px 12px;border-radius:999px;display:inline-block;margin:4px;font-weight:900'>🔗 /directo</a></div></body></html>"
    return HTMLResponse(html_resp)

@app.post("/chat")
async def chat_endpoint(req: ChatReq, request: Request):
    try:
        ip=request.client.host if request.client else "?"
        if not check_rate(ip): return JSONResponse({"respuesta":"Vas rapido, espera 1s"}, status_code=429)
        sid=get_session(req.session_id)
        r=cerebro(req.message)
        try:
            sesiones_mem[sid].append({"u":req.message[:200],"b":r[:500],"fecha":datetime.now().isoformat()})
            persist_session(sid)
        except: pass
        return {"respuesta": r}
    except Exception as e:
        return JSONResponse({"respuesta": "Error: "+str(e)}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT",8000)))
