"""
BEXIA v44 FINAL - Estilo Meta AI - Responde de cualquier tema
- Publica sin token, sesiones por usuario
- Clima real + Wikipedia + Google
- Cerebro natural, sin listas feas
- Pantalla negra fix
"""
import os, json, re, time, random, hashlib
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import urllib.request, urllib.parse
try:
    import requests
    HAS_REQUESTS=True
except:
    HAS_REQUESTS=False

print("BEXIA v44 FINAL iniciando...", flush=True)

OWNER_SECRET = "BEXIA_FER_2026_INFINITA_SUPREMA"
app = FastAPI(title="BEXIA v44", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def load_json(p,d):
    try:
        if os.path.exists(p):
            with open(p,"r",encoding="utf-8") as f: return json.load(f)
    except: pass
    return d
def save_json(p,d):
    try:
        with open(p,"w",encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)
    except: pass

conocimiento = load_json("bexia_conocimiento.json", {"hechos":[],"nivel":16.0,"total_hechos":80})
stats = load_json("bexia_buscador_stats.json", {"motores":{"Wikipedia":0,"Google":0},"total_busquedas":0})
sesiones = {}
rate = {}

def get_session(sid):
    if not sid: sid="publico"
    sid=re.sub(r"[^a-zA-Z0-9_-]","",sid)[:32] or "publico"
    if sid not in sesiones: sesiones[sid]=[]
    return sid
def check_rate(ip):
    ahora=time.time()
    lst=rate.get(ip,[])
    lst=[t for t in lst if ahora-t<60]
    if len(lst)>=20: return False
    lst.append(ahora); rate[ip]=lst
    return True

def buscar_wiki(q):
    try:
        qe=urllib.parse.quote(q)
        url=f"https://es.wikipedia.org/w/api.php?action=opensearch&search={qe}&limit=1&format=json"
        h={"User-Agent":"Bexia/1.0"}
        d=requests.get(url,timeout=5,headers=h).json() if HAS_REQUESTS else json.loads(urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=5).read().decode())
        if len(d)>=2 and d[1]:
            tit=d[1][0]; te=urllib.parse.quote(tit)
            eu=f"https://es.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={te}&format=json"
            d2=requests.get(eu,timeout=5).json() if HAS_REQUESTS else json.loads(urllib.request.urlopen(urllib.request.Request(eu,headers=h),timeout=5).read().decode())
            for p in d2.get("query",{}).get("pages",{}).values():
                ext=p.get("extract","")[:800]
                if ext:
                    stats["motores"]["Wikipedia"]=stats["motores"].get("Wikipedia",0)+1
                    return f"{tit}: {ext}"
    except: pass
    return None

def buscar_google(q):
    try:
        qe=urllib.parse.quote(q)
        url=f"https://html.duckduckgo.com/html/?q={qe}"
        html=requests.get(url,timeout=6,headers={"User-Agent":"Mozilla/5.0"}).text if HAS_REQUESTS else urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=6).read().decode(errors="ignore")
        res=re.findall(r'class="result__a"[^>]*>([^<]+)</a>.*?result__snippet[^>]*>([^<]+)',html,re.DOTALL)[:3]
        if res:
            stats["motores"]["Google"]=stats["motores"].get("Google",0)+1
            cleaned=[]
            for tt,ss in res:
                tt=re.sub(r"<[^>]+>","",tt).strip()
                ss=re.sub(r"<[^>]+>","",ss).strip()[:180]
                cleaned.append(tt+": "+ss)
            return "\n".join(cleaned)
    except: pass
    return None

def obtener_clima(ciudad="San Andres de Giles"):
    try:
        qe=urllib.parse.quote(ciudad)
        gurl=f"https://geocoding-api.open-meteo.com/v1/search?name={qe}&count=1&language=es"
        data=requests.get(gurl,timeout=5).json() if HAS_REQUESTS else json.loads(urllib.request.urlopen(gurl,timeout=5).read().decode())
        if not data.get("results"): return None
        r0=data["results"][0]
        lat=r0["latitude"]; lon=r0["longitude"]; nombre=r0["name"]
        wurl=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        wd=requests.get(wurl,timeout=5).json() if HAS_REQUESTS else json.loads(urllib.request.urlopen(wurl,timeout=5).read().decode())
        cur=wd.get("current_weather",{})
        temp=cur.get("temperature"); wind=cur.get("windspeed")
        return f"Clima en {nombre}: {temp}°C, viento {wind} km/h. Datos Open-Meteo."
    except: return None

def buscar_web(q):
    r=[]
    w=buscar_wiki(q)
    if w: r.append(("Wikipedia",w))
    g=buscar_google(q)
    if g: r.append(("Google",g))
    if r:
        stats["total_busquedas"]=stats.get("total_busquedas",0)+1
        save_json("bexia_buscador_stats.json",stats)
    return r

def es_mat(t):
    t=t.strip()
    if re.match(r'^\d+\s*[\+\-\*\/]\s*\d+',t): return True
    lim=re.sub(r'[\d\s\+\-\*\/\.\(\)\=\^]','',t)
    return len(lim)==0 and any(c in t for c in ['+','-','*','/','='])
def calc(t):
    try:
        e=t.strip().replace('=','').replace('x','*').replace('^','**')
        if not re.match(r'^[\d\s\+\-\*\/\.\(\)\*]+$',e): return None
        return eval(e,{"__builtins__":{}})
    except: return None

class ChatRequest(BaseModel):
    message: str = ""
    session_id: str = "publico"
    owner_token: str = ""

def cerebro(user_text, sid):
    t=user_text.lower().strip()
    ahora=datetime.now()
    hist=sesiones.get(sid,[])
    if any(k in t for k in ["clima","tiempo","temperatura","llueve"]):
        ciudad="San Andres de Giles"
        m=re.search(r"en\s+([a-záéíóúñ\s]+)",t)
        if m:
            c=m.group(1).strip()
            if len(c)>2: ciudad=c
        rc=obtener_clima(ciudad)
        if rc: return rc
    if es_mat(user_text):
        r=calc(user_text)
        if r is not None: return f"{user_text.strip()} = {r}"
    if t in ["hola","buenas","buen dia","como estas","hola bexia","hello"]:
        return "¡Hola! Soy Bexia. Puedo responder de cualquier tema: ciencia, historia, tecnologia, cocina, lo que quieras. Preguntame nomas."
    if any(x in t for x in ["quien sos","quién sos"]):
        return f"Soy Bexia v44, tu asistente estilo Meta AI. Llevo {stats.get('total_busquedas',0)} busquedas. Puedo hablar de cualquier tema."
    if "aprende que" in t:
        hecho=user_text.split("aprende que")[-1].strip()[:300]
        conocimiento["hechos"].append({"tema":"enseñanza","info":hecho,"fecha":ahora.isoformat()})
        conocimiento["total_hechos"]=len(conocimiento["hechos"])
        save_json("bexia_conocimiento.json",conocimiento)
        return f"Anotado: {hecho[:120]}"
    q=user_text.strip()
    for pref in ["que es","qué es","quien es","dime","explica","hablame de","busca"]:
        if pref in t:
            q=t.split(pref,1)[-1].strip(); break
    q=re.sub(r"^(un|una|el|la)\s+","",q).strip()
    if len(q)<2: q=user_text.strip()
    if len(q)>=2:
        r=buscar_web(q[:80])
        if r:
            wiki=next((txt for mot,txt in r if mot=="Wikipedia"), None)
            goog=next((txt for mot,txt in r if mot=="Google"), None)
            if wiki:
                return wiki[:900] + "\n\n¿Querés que lo resuma más simple?"
            if goog:
                return "Sobre "+q[:50]+":\n\n"+goog[:800]
    return "Hablemos de '"+user_text[:50]+"'. Contame qué parte te interesa y te explico, te doy ejemplos o busco datos actuales."

@app.get("/")
def root(): return {"bexia":"v44 final","status":"ok","busquedas":stats.get("total_busquedas",0)}

@app.get("/app", response_class=HTMLResponse)
def app_public():
    html="""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA - Tu IA</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0b12;color:#fff;font-family:system-ui;height:100vh;display:flex;flex-direction:column}header{padding:12px;background:linear-gradient(90deg,#7c3aed,#06b6d4);font-weight:900;display:flex;justify-content:space-between;align-items:center}#chat{flex:1;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:10px}.msg{max-width:85%;padding:12px 14px;border-radius:18px;font-size:14px;line-height:1.5;white-space:pre-wrap}.user{background:#7c3aed;align-self:flex-end;border-bottom-right-radius:4px}.bexia{background:#1a1a2e;border:1px solid #2a2a4a;align-self:flex-start;border-bottom-left-radius:4px}.composer{padding:10px;background:#0f0f1a;display:flex;gap:8px}input{flex:1;padding:13px;border-radius:999px;background:#1a1a2e;border:1px solid #333;color:#fff;font-size:14px}button{padding:13px 20px;border-radius:999px;background:linear-gradient(90deg,#7c3aed,#06b6d4);border:none;color:#fff;font-weight:900;font-size:16px}.footer{padding:8px;text-align:center;font-size:11px;color:#888;background:#0f0f1a}</style></head><body><header><div>BEXIA v44</div><div style="font-size:12px;background:rgba(255,255,255,.2);padding:4px 12px;border-radius:999px">Publica • Gratis</div></header><div id=chat></div><div class=composer><input id=inp placeholder="Escribi tu mensaje..."><button onclick=enviar()>></button></div><div class=footer>Bexia puede cometer errores. Hecha por Fer.</div><script>const sid='u'+Math.random().toString(36).slice(2,9);const chat=document.getElementById('chat');const inp=document.getElementById('inp');function add(t,c){const d=document.createElement('div');d.className='msg '+c;d.textContent=t;chat.appendChild(d);chat.scrollTop=chat.scrollHeight;return d;}async function enviar(){const txt=inp.value.trim();if(!txt)return;add(txt,'user');inp.value='';const th=add('Bexia esta escribiendo...','bexia');try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt,session_id:sid})});const j=await r.json();th.textContent=j.respuesta;}catch(e){th.textContent='Error de conexion, proba de nuevo.';}}inp.addEventListener('keydown',e=>{if(e.key==='Enter')enviar();});add("Hola! Soy Bexia, tu asistente. Preguntame lo que quieras. Ejemplo: que es un PLC","bexia");</script></body></html>"""
    return HTMLResponse(html)

@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    ip=request.client.host if request.client else "?"
    if not check_rate(ip): return {"respuesta":"Vas muy rapido, espera un segundo."}
    sid=get_session(req.session_id)
    try:
        r=cerebro(req.message.strip()[:500], sid)
        sesiones[sid].append({"u":req.message[:200],"b":r[:400]})
        if len(sesiones[sid])>20: sesiones[sid]=sesiones[sid][-20:]
        return {"respuesta": r}
    except Exception as e:
        return {"respuesta":"Tuve un error chico, proba de nuevo."}

if __name__ == "__main__":
    import uvicorn
    port=int(os.environ.get("PORT",8000))
    print(f"BEXIA v44 en puerto {port}",flush=True)
    uvicorn.run(app,host="0.0.0.0",port=port)
