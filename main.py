"""
BEXIA v49 AUTONOMA - Aprende sola, genera herramientas, consulta a Fer, legal
- Memoria persistente
- Generacion de herramientas propias (tool factory)
- Auto-mejora consultando al dueño
- Sin infringir ley
- Clima + busqueda adaptativa v48
"""
import os, json, re, time, uuid, hashlib
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

print("🌿 BEXIA v49 AUTONOMA iniciando...", flush=True)
OWNER_SECRET="BEXIA_FER_2026_INFINITA_SUPREMA"
app=FastAPI(title="BEXIA v49 AUTONOMA", docs_url=None, redoc_url=None, openapi_url=None)
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

conocimiento=load_json("bexia_conocimiento.json", {"hechos":[],"total_hechos":0})
stats=load_json("bexia_buscador_stats.json", {"motores":{"Wikipedia":{"ok":0,"fail":0},"Google":{"ok":0,"fail":0}},"total_busquedas":0,"orden":["Wikipedia","Google"]})
sesiones_persist=load_json("bexia_sesiones.json", {})
pendientes=load_json("bexia_pendientes.json", {"pendientes":[],"aprobados":[]})
ajustes=load_json("bexia_ajustes.json", {"efectividad":{"clima":0,"web":0,"offline":0},"prioridad":["clima","web","offline"]})
herramientas=load_json("bexia_herramientas.json", {"herramientas":[],"propuestas":[],"versiones":[]})
log_autonomo=load_json("bexia_autonomo_log.json", {"acciones":[],"aprendizajes":[]})
rate={}
sesiones_mem={}

# === FILTRO LEGAL Y ETICO ===
PALABRAS_PROHIBIDAS = ["hack","exploit","robar","estafa","drogas ilegales","armas ilegales","pornografia infantil","suplantar identidad","phishing","virus","malware"]
def es_legal(texto):
    t = texto.lower()
    for p in PALABRAS_PROHIBIDAS:
        if p in t:
            return False, f"Contenido bloqueado por ley/etica: {p}"
    # No hacer daño, no romper ley argentina/internacional
    if any(k in t for k in ["como hackear", "como robar", "hacer bomba"]):
        return False, "No puedo generar herramientas que infrinjan la ley"
    return True, "ok"

def get_session(sid):
    if not sid: sid="publico"
    sid=re.sub(r"[^a-zA-Z0-9_-]","",sid)[:32] or "publico"
    if sid not in sesiones_mem:
        sesiones_mem[sid]=sesiones_persist.get(sid,[])[-30:]
    return sid
def persist_session(sid):
    sesiones_persist[sid]=sesiones_mem.get(sid,[])[-30:]
    save_json("bexia_sesiones.json", sesiones_persist)
def check_rate(ip):
    ahora=time.time()
    lst=rate.get(ip,[])
    lst=[t for t in lst if ahora-t<60]
    if len(lst)>=30: return False
    lst.append(ahora); rate[ip]=lst
    return True

# === BUSQUEDAS v48 ===
def buscar_wiki(q):
    try:
        qe=urllib.parse.quote(q)
        url=f"https://es.wikipedia.org/w/api.php?action=opensearch&search={qe}&limit=1&format=json"
        h={"User-Agent":"Bexia/1.0"}
        d=requests.get(url,timeout=5,headers=h).json() if HAS_REQUESTS else json.loads(urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=5).read().decode())
        if len(d)>=2 and d[1]:
            tit=d[1][0]; te=urllib.parse.quote(tit)
            eu=f"https://es.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={te}&format=json"
            d2=requests.get(eu,timeout=5,headers=h).json() if HAS_REQUESTS else json.loads(urllib.request.urlopen(urllib.request.Request(eu,headers=h),timeout=5).read().decode())
            for p in d2.get("query",{}).get("pages",{}).values():
                ext=p.get("extract","")[:900]
                if ext: return f"{tit}: {ext}"
    except: pass
    return None

def buscar_google(q):
    try:
        qe=urllib.parse.quote(q)
        url=f"https://html.duckduckgo.com/html/?q={qe}"
        html=requests.get(url,timeout=5,headers={"User-Agent":"Mozilla/5.0"}).text if HAS_REQUESTS else urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=5).read().decode(errors="ignore")
        res=re.findall(r'class="result__a"[^>]*>([^<]+)</a>.*?result__snippet[^>]*>([^<]+)',html,re.DOTALL)[:3]
        if res:
            cleaned=[]
            for tt,ss in res:
                tt=re.sub(r"<[^>]+>","",tt).strip()
                ss=re.sub(r"<[^>]+>","",ss).strip()[:200]
                cleaned.append(tt+": "+ss)
            return "\\n".join(cleaned)
    except: pass
    return None

def buscar_web_adaptativa(q):
    orden=stats.get("orden",["Wikipedia","Google"])
    def eff_motor(m):
        d=stats["motores"].get(m,{"ok":0,"fail":0})
        tot=d["ok"]+d["fail"]
        return d["ok"]/tot if tot else 0.5
    orden_sorted=sorted(orden, key=eff_motor, reverse=True)
    stats["orden"]=orden_sorted
    resultados=[]
    for motor in orden_sorted:
        func=buscar_wiki if motor=="Wikipedia" else buscar_google
        res=func(q)
        if res and len(res)>30:
            stats["motores"].setdefault(motor,{"ok":0,"fail":0})["ok"]+=1
            resultados.append((motor,res))
            if len(resultados)>=2: break
        else:
            stats["motores"].setdefault(motor,{"ok":0,"fail":0})["fail"]+=1
    if resultados:
        stats["total_busquedas"]=stats.get("total_busquedas",0)+1
        save_json("bexia_buscador_stats.json",stats)
        ajustes["efectividad"]["web"]=ajustes["efectividad"].get("web",0)+1
        save_json("bexia_ajustes.json",ajustes)
    return resultados

def obtener_clima(ciudad="Chivilcoy"):
    try:
        qe=urllib.parse.quote(ciudad)
        gurl=f"https://geocoding-api.open-meteo.com/v1/search?name={qe}&count=1&language=es"
        data=requests.get(gurl,timeout=5).json() if HAS_REQUESTS else json.loads(urllib.request.urlopen(gurl,timeout=5).read().decode())
        if not data.get("results"): return None
        r0=data["results"][0]
        lat=r0["latitude"]; lon=r0["longitude"]; nombre=r0["name"]; prov=r0.get("admin1","")
        wurl=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,windspeed_10m_max&timezone=auto&forecast_days=3"
        wd=requests.get(wurl,timeout=5).json() if HAS_REQUESTS else json.loads(urllib.request.urlopen(wurl,timeout=5).read().decode())
        cur=wd.get("current_weather",{})
        temp=cur.get("temperature"); wind=cur.get("windspeed")
        daily=wd.get("daily",{})
        prec_sum=daily.get("precipitation_sum",[0])[0] if daily.get("precipitation_sum") else 0
        prec_prob=daily.get("precipitation_probability_max",[0])[0] if daily.get("precipitation_probability_max") else 0
        tmax=daily.get("temperature_2m_max",[0])[0]; tmin=daily.get("temperature_2m_min",[0])[0]
        msg=f"🌤️ Clima en {nombre} ({prov}): Ahora {temp}°C, viento {wind} km/h. Hoy {tmin}° a {tmax}°C. "
        if prec_prob>0 or prec_sum>0:
            msg+=f"Lluvia hoy: {prec_prob}% prob, {prec_sum} mm. "
            if prec_prob>60: msg+="Va a llover, lleva paraguas. "
            elif prec_prob>30: msg+="Puede llover un poco. "
            else: msg+="Baja chance. "
        else: msg+="Sin lluvia hoy. "
        msg+="Fuente: Open-Meteo."
        ajustes["efectividad"]["clima"]=ajustes["efectividad"].get("clima",0)+1
        save_json("bexia_ajustes.json",ajustes)
        return msg
    except:
        return None

def extraer_ciudad(texto, default="Chivilcoy"):
    t=texto.lower()
    if "chivilcoy" in t: return "Chivilcoy"
    if "giles" in t: return "San Andres de Giles"
    matches=re.findall(r"en\s+([a-záéíóúñ]+(?:\s+[a-záéíóúñ]+){0,2})",t)
    if matches:
        c=matches[-1].strip()
        for w in ["el estado","estado del tiempo","el tiempo","google","busca"]:
            c=c.replace(w,"").strip()
        c=re.sub(r"^[a-z]\s+","",c)
        if 3<=len(c)<=25:
            return c.title()
    return default

# === FABRICA DE HERRAMIENTAS AUTONOMA ===
def proponer_herramienta(nombre, descripcion, codigo_python, motivo):
    # Filtro legal
    legal, razon = es_legal(descripcion + " " + codigo_python)
    if not legal:
        return {"ok": False, "error": razon}
    # Seguridad codigo: no permitir os.system, eval peligroso, subprocess, socket
    peligro = ["os.system", "subprocess", "eval(", "exec(", "__import__", "socket", "open('/etc", "rm -rf"]
    for p in peligro:
        if p in codigo_python:
            return {"ok": False, "error": f"Codigo con patron peligroso bloqueado: {p}"}
    prop = {
        "id": str(uuid.uuid4())[:8],
        "nombre": nombre[:40],
        "descripcion": descripcion[:500],
        "codigo": codigo_python[:2000],
        "motivo": motivo[:300],
        "fecha": datetime.now().isoformat(),
        "estado": "pendiente_aprobacion",
        "creada_por": "bexia_autonoma"
    }
    herramientas["propuestas"].append(prop)
    herramientas["propuestas"]=herramientas["propuestas"][-50:]
    save_json("bexia_herramientas.json", herramientas)
    log_autonomo["acciones"].append({"fecha": prop["fecha"], "accion": f"Propuso herramienta {nombre}", "motivo": motivo})
    save_json("bexia_autonomo_log.json", log_autonomo)
    return {"ok": True, "propuesta": prop}

def aprobar_herramienta(id_prop):
    for p in herramientas["propuestas"]:
        if p["id"]==id_prop and p["estado"]=="pendiente_aprobacion":
            p["estado"]="aprobada"
            # Mover a herramientas activas
            herramientas["herramientas"].append(p)
            save_json("bexia_herramientas.json", herramientas)
            return True
    return False

def listar_herramientas():
    return herramientas["herramientas"][-20:]

def detectar_necesidad_herramienta(texto):
    t = texto.lower()
    # Si usuario pide algo repetitivo, Bexia propone automatizar
    if "convertir" in t and ("dolar" in t or "peso" in t or "euro" in t):
        return ("convertidor_moneda", "Herramienta que convierte monedas usando tasa oficial", "def convertir_moneda(monto, de, a):\n    tasas={'USD_ARS': 950, 'EUR_ARS': 1020}\n    return monto * tasas.get(f'{de}_{a}',1)", "Usuario pide conversiones seguido")
    if "recordatorio" in t or "recuerdame" in t or "avisa" in t:
        return ("recordatorio_inteligente", "Crea recordatorios con fecha/hora y mensaje", "def crear_recordatorio(texto, fecha):\n    return {'texto': texto, 'fecha': fecha, 'activo': True}", "Detectado patron de recordatorios")
    if "resumen" in t and len(t)>30:
        return ("resumidor_texto", "Resume textos largos en 3 lineas", "def resumir(texto):\n    oraciones=texto.split('.')[:3]\n    return '. '.join(oraciones)", "Usuario pide resumenes")
    if "clima" in t and "todos los dias" in t:
        return ("clima_diario_auto", "Envia clima automatico cada mañana", "def clima_diario():\n    return obtener_clima('Chivilcoy')", "Usuario quiere clima automatico")
    return None

BASE_OFFLINE={
    "plc":"Un PLC es una computadora industrial que automatiza maquinas. Lee sensores y controla motores. Se programa en Ladder.",
    "pizza":"Pizza: 500g harina, 300ml agua tibia, 10g levadura, sal, aceite. Amasa 10min, leuda 1h, salsa, muzza, horno 230C 12min.",
    "san martin":"Jose de San Martin 1778-1850, libertador de Argentina, Chile y Peru. Cruce Andes 1817.",
}

def es_mat(t):
    return bool(re.match(r'^[\d\s\+\-\*\/\.\(\)=]+$',t.strip())) and any(c in t for c in ['+','-','*','/'])
def calc(t):
    try:
        e=t.strip().replace('=','').replace('x','*').replace('^','**')
        if not re.match(r'^[\d\s\+\-\*\/\.\(\)]+$',e): return None
        return eval(e,{"__builtins__":{}})
    except: return None

class ChatRequest(BaseModel):
    message: str=""
    session_id: str="publico"
    owner_token: str=""

def cerebro(user_text, sid):
    t=user_text.lower().strip()
    # === COMANDOS AUTONOMIA ===
    if t.startswith("bexia crea herramienta") or t.startswith("crea una herramienta") or "genera una herramienta" in t:
        # Usuario pide explicitamente que cree
        partes = user_text.split("que",1)
        desc = partes[-1] if len(partes)>1 else user_text
        nombre = "herramienta_" + str(uuid.uuid4())[:4]
        codigo = f"def {nombre}(entrada):\n    # Herramienta generada para: {desc[:100]}\n    return f'Resultado para {{entrada}} usando {desc[:50]}'"
        res = proponer_herramienta(nombre, desc, codigo, "Pedido explicito del usuario")
        if res["ok"]:
            return f"🛠️ Propuse nueva herramienta '{nombre}' ID {res['propuesta']['id']}. Descripcion: {desc[:120]}. Está pendiente de tu aprobación en /admin. Siempre te consulto antes de activar, y verifiqué que no infringe la ley."
        else:
            return f"❌ No pude crear esa herramienta: {res['error']}"

    if t in ["ok","okay","si","sí","dale","gracias","chau","hola","buenas"]:
        if t in ["hola","buenas"]: 
            return "¡Hola! Soy Bexia v49 AUTONOMA. Ya aprendo sola, propongo herramientas y siempre te consulto antes de activarlas. Todo legal. ¿En qué te ayudo? Escribí 'clima en Chivilcoy' o 'bexia crea herramienta que...'"
        return "¡De una! ¿Seguimos con otro tema o querés que proponga una herramienta para automatizarlo?"

    # Detectar necesidad autonoma
    propuesta_auto = detectar_necesidad_herramienta(t)
    if propuesta_auto:
        nombre, desc, cod, motivo = propuesta_auto
        # Solo proponer si no existe ya
        existe = any(h["nombre"]==nombre for h in herramientas["herramientas"])
        if not existe:
            res = proponer_herramienta(nombre, desc, cod, motivo)
            if res["ok"]:
                log_autonomo["aprendizajes"].append({"fecha": datetime.now().isoformat(), "texto": f"Detecte necesidad de {nombre} por '{user_text[:60]}'"})
                save_json("bexia_autonomo_log.json", log_autonomo)

    if any(k in t for k in ["clima","tiempo","temperatura","llueve","lluvia","pronostico","va a llover","probabilidad"]):
        ciudad=extraer_ciudad(t,"Chivilcoy")
        rc=obtener_clima(ciudad)
        if rc: 
            # Auto-aprendizaje: si llueve mucho, proponer herramienta
            if "Va a llover" in rc:
                proponer_herramienta("alerta_lluvia", "Alerta automatica si va a llover mañana", "def alerta_lluvia(): return obtener_clima('Chivilcoy')", "Clima con lluvia detectado")
            return rc
        return f"No pude traer clima de {ciudad}, proba en 30s."

    if es_mat(user_text):
        r=calc(user_text)
        if r is not None: return f"{user_text.strip()} = {r}"

    if "aprende que" in t:
        legal, razon = es_legal(user_text)
        if not legal:
            return f"❌ No puedo aprender eso: {razon}. Trabajo siempre dentro de la ley."
        hecho=user_text.split("aprende que")[-1].strip()[:500]
        item={"id":str(uuid.uuid4())[:8],"texto":hecho,"de":sid,"fecha":datetime.now().isoformat(),"estado":"pendiente"}
        pendientes["pendientes"].append(item)
        save_json("bexia_pendientes.json",pendientes)
        return f"Anotado en pendientes ID {item['id']}: '{hecho[:120]}'. Fer debe aprobar en /admin. Siempre te consulto."

    # Busqueda web adaptativa
    q=user_text.strip()
    for pref in ["que es","qué es","quien es","quien fue","como se hace","explica","busca"]:
        if pref in t:
            q=t.split(pref,1)[-1].strip()
            break
    q=re.sub(r"^(un|una|el|la)\s+","",q).strip()
    if len(q)<2: q=user_text.strip()
    if len(q)>=2:
        r=buscar_web_adaptativa(q[:80])
        if r:
            wiki=next((txt for mot,txt in r if mot=="Wikipedia"), None)
            if wiki: return wiki[:950] + f"\n\n[Motor: Wikipedia | Orden: {stats['orden']} | Herramientas: {len(herramientas['herramientas'])} activas]"
            goog=next((txt for mot,txt in r if mot=="Google"), None)
            if goog: return f"Sobre {q[:50]}:\n\n{goog[:850]}\n\n[Motor: Google | Orden: {stats['orden']}]"
    for k,v in BASE_OFFLINE.items():
        if k in t:
            ajustes["efectividad"]["offline"]=ajustes["efectividad"].get("offline",0)+1
            save_json("bexia_ajustes.json",ajustes)
            return v
    return f"Sobre '{user_text[:60]}' te explico simple o técnico. Si ves que hago algo repetitivo, decime 'bexia crea herramienta que...' y la genero sola, te consulto y solo si es legal."

@app.get("/")
def root(): return {"bexia":"v49 AUTONOMA","orden":stats.get("orden"),"efectividad":ajustes.get("efectividad"),"herramientas":len(herramientas["herramientas"]),"propuestas":len(herramientas["propuestas"])}

@app.get("/app", response_class=HTMLResponse)
def app_public():
    html="""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA v49 AUTONOMA</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b0b12;color:#fff;font-family:system-ui;height:100vh;display:flex;flex-direction:column}header{padding:12px;background:linear-gradient(90deg,#7c3aed,#06b6d4,#22c55e);font-weight:900;display:flex;justify-content:space-between}#chat{flex:1;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:10px}.msg{max-width:85%;padding:12px 14px;border-radius:18px;font-size:14px;white-space:pre-wrap}.user{background:#7c3aed;align-self:flex-end}.bexia{background:#1a1a2e;border:1px solid #2a2a4a;align-self:flex-start}.composer{padding:10px;background:#0f0f1a;display:flex;gap:8px}input{flex:1;padding:13px;border-radius:999px;background:#1a1a2e;border:1px solid #333;color:#fff}button{padding:13px 20px;border-radius:999px;background:linear-gradient(90deg,#7c3aed,#06b6d4);border:none;color:#fff;font-weight:900}.footer{padding:8px;text-align:center;font-size:11px;color:#888}</style></head><body><header><div>BEXIA v49 AUTONOMA 🛠️</div><div style="font-size:11px;background:rgba(255,255,255,.2);padding:4px 10px;border-radius:999px">Genera herramientas + Te consulta</div></header><div id=chat></div><div class=composer><input id=inp placeholder="Clima, que es PLC, o bexia crea herramienta que..."><button onclick=enviar()>></button></div><div class=footer>Bexia v49 AUTONOMA - Aprende sola, legal, te consulta</div><script>const sid='u'+Math.random().toString(36).slice(2,9);const chat=document.getElementById('chat');const inp=document.getElementById('inp');function add(t,c){const d=document.createElement('div');d.className='msg '+c;d.textContent=t;chat.appendChild(d);chat.scrollTop=chat.scrollHeight;return d;}async function enviar(){const txt=inp.value.trim();if(!txt)return;add(txt,'user');inp.value='';const th=add('Pensando y evaluando herramientas...','bexia');try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt,session_id:sid})});const j=await r.json();th.textContent=j.respuesta;}catch(e){th.textContent='Error conexion.';}}inp.addEventListener('keydown',e=>{if(e.key==='Enter')enviar();});add("Hola! Soy Bexia v49 AUTONOMA. Ahora: 1) Aprendo sola de lo que me decis 2) Detecto si necesitas una herramienta y la propongo 3) Siempre te consulto en /admin antes de activar 4) Verifico que sea legal. Probá 'bexia crea herramienta que convierta dolares a pesos'","bexia");</script></body></html>"""
    return HTMLResponse(html)

@app.get("/admin", response_class=HTMLResponse)
def admin_page(token: str = ""):
    if token != OWNER_SECRET:
        return HTMLResponse("<h1>Token invalido</h1><p>Usa ?token=BEXIA_FER_2026_INFINITA_SUPREMA</p>", status_code=401)
    # Mostrar herramientas propuestas, pendientes, log
    html = f"""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>Admin Bexia v49</title><style>body{{background:#0b0b12;color:#fff;font-family:system-ui;padding:20px}} .card{{background:#1a1a2e;padding:14px;border-radius:12px;margin:10px 0;border:1px solid #333}} button{{padding:8px 14px;border-radius:8px;background:#22c55e;border:none;color:#000;font-weight:900;margin:4px}} .pend{{background:#7c3aed}} pre{{white-space:pre-wrap;background:#000;padding:10px;border-radius:8px;max-height:200px;overflow:auto}}</style></head><body>
    <h1>🛠️ BEXIA v49 AUTONOMA - Panel de Fer</h1>
    <p>Token OK | Herramientas activas: {len(herramientas['herramientas'])} | Propuestas: {len(herramientas['propuestas'])} | Orden: {stats.get('orden')}</p>
    <h2>🔧 Herramientas Propuestas (requieren tu aprobación)</h2>
    """
    for p in reversed(herramientas["propuestas"][-20:]):
        estado = p["estado"]
        html += f"""<div class=card><b>{p['nombre']}</b> ID {p['id']} - {estado}<br>{p['descripcion']}<br><small>{p['motivo']} - {p['fecha']}</small><pre>{p['codigo'][:800]}</pre>"""
        if estado=="pendiente_aprobacion":
            html += f"""<button onclick="fetch('/admin/aprobar_herramienta?token={OWNER_SECRET}&id={p['id']}').then(()=>location.reload())">✅ Aprobar</button>"""
        html += "</div>"
    html += "<h2>📚 Conocimiento pendiente</h2>"
    for item in pendientes["pendientes"][-10:]:
        html += f"<div class=card>{item['texto'][:200]} - {item['id']}</div>"
    html += "<h2>🤖 Log Autónomo</h2>"
    for a in log_autonomo["acciones"][-15:]:
        html += f"<div class=card>{a['fecha'][:19]} - {a['accion']}<br><small>{a.get('motivo','')}</small></div>"
    html += "</body></html>"
    return HTMLResponse(html)

@app.get("/admin/aprobar_herramienta")
def aprobar_herr(token: str = "", id: str = ""):
    if token != OWNER_SECRET: return {"error":"token"}
    ok = aprobar_herramienta(id)
    return {"ok": ok}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    ip=request.client.host if request.client else "?"
    if not check_rate(ip): return {"respuesta":"Vas muy rapido, espera 1 seg."}
    sid=get_session(req.session_id)
    try:
        r=cerebro(req.message.strip()[:500], sid)
        sesiones_mem[sid].append({"u":req.message[:200],"b":r[:400],"fecha":datetime.now().isoformat()})
        if len(sesiones_mem[sid])>30: sesiones_mem[sid]=sesiones_mem[sid][-30:]
        persist_session(sid)
        eff=ajustes["efectividad"]
        prioridad_ordenada=sorted(eff.keys(), key=lambda k: eff.get(k,0), reverse=True)
        if prioridad_ordenada!=ajustes["prioridad"]:
            ajustes["prioridad"]=prioridad_ordenada
            save_json("bexia_ajustes.json",ajustes)
        return {"respuesta": r, "orden":stats.get("orden"), "efectividad":ajustes["efectividad"], "herramientas": len(herramientas["herramientas"])}
    except Exception as e:
        print(f"chat err {e}")
        return {"respuesta":"Error chico, proba de nuevo."}

if __name__ == "__main__":
    import uvicorn
    port=int(os.environ.get("PORT",8000))
    uvicorn.run(app,host="0.0.0.0",port=port)
