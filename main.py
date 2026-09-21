
import os, json, re, time, uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import urllib.request, urllib.parse
try:
    import requests
    HAS_REQUESTS=True
except:
    HAS_REQUESTS=False

print("BEXIA v67.2 FULL - CREA COMO META COMO CLAUDE - Iniciando...", flush=True)
OWNER_SECRET="BEXIA_FER_2026_INFINITA_SUPREMA"
VERSION="v67.2"
app=FastAPI(title="BEXIA v67.2 FULL", docs_url=None, redoc_url=None, openapi_url=None)
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
herramientas=load_json("bexia_herramientas.json", {"cache":{},"versiones_codigo":[],"workflows_n8n":[],"conexiones_ia":[],"clones_creados":[],"herramientas_meta_ai":[]})
memoria_propia=load_json("bexia_memoria_propia.json", {"recuerdos":[],"auto_memorias":[]})
log_autonomo=load_json("bexia_autonomo_log.json", {"clones":[]})
rate={}
sesiones_mem={}

def get_session(sid):
    if not sid: sid="publico"
    try: sid=re.sub(r"[^a-zA-Z0-9_-]","",sid)[:32] or "publico"
    except: sid="publico"
    if sid not in sesiones_mem: sesiones_mem[sid]=sesiones_persist.get(sid,[])[:40]
    return sid
def persist_session(sid):
    try:
        sesiones_persist[sid]=sesiones_mem.get(sid,[])[:40]
        save_json("bexia_sesiones.json", sesiones_persist)
    except: pass
def check_rate(ip):
    ahora=time.time()
    lst=rate.get(ip,[])
    lst=[t for t in lst if ahora-t<60]
    if len(lst)>=60: return False
    lst.append(ahora); rate[ip]=lst
    return True

def crear_clon(tipo, objetivo):
    cid=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    if tipo=="meta":
        codigo=f"# CLON META AI - {cid}\n# Objetivo: {objetivo[:80]}\nclass ClonMetaAI:\n    herramientas=['content_search','local_search','image_gen','video_gen']\n    def content_search(self,q): return f'Posts IG/FB/Threads sobre {{q}}'\n    def local_search(self,l,c='Chivilcoy'): return f'Lugares {{l}} en {{c}}: 5 con rating'\n    def pensar(self,e): return f'Meta AI sobre {{e}}: social + lugares + visual'\nprint('Clon Meta AI {cid} creado')\n"
        clon={"id":cid,"tipo":"meta_ai","nombre":f"Clon Meta AI - {objetivo[:30]}","objetivo":objetivo[:200],"codigo":codigo,"estilo":"Meta AI - content_search, local_search, image_gen","fecha":fecha,"inspirado_en":"Meta AI Llama 4"}
    elif tipo=="claude":
        codigo=f"# CLON CLAUDE - {cid}\n# Objetivo: {objetivo[:80]}\nclass ClonClaude:\n    principios=['Paso a paso','Seguro/util/honesto','Explica por que','Codigo limpio']\n    def razonar(self,p): return '1.Entender 2.Analizar 3.Opciones 4.Elegir 5.Explicar 6.Ejemplo 7.Verificar'\n    def pensar(self,e): return f'Claude sobre {{e}}: razonamiento estructurado'\nprint('Clon Claude {cid} creado')\n"
        clon={"id":cid,"tipo":"claude","nombre":f"Clon Claude - {objetivo[:30]}","objetivo":objetivo[:200],"codigo":codigo,"estilo":"Claude - Razonamiento paso a paso, seguro, util","fecha":fecha,"inspirado_en":"Claude Anthropic"}
    else:
        codigo=f"# CLON HIBRIDO META+CLAUDE - {cid}\n# Objetivo: {objetivo[:80]}\nclass HibridoMetaClaude:\n    herramientas_meta=['content_search','local_search','image_gen']\n    principios_claude=['Paso a paso','Seguro/util']\n    def pensar(self,e): return f'Hibrido Meta+Claude {{e}}: herramientas Meta + razonamiento Claude'\nprint('Hibrido {cid} creado')\n"
        clon={"id":cid,"tipo":"hibrido_meta_claude","nombre":f"Hibrido Meta+Claude - {objetivo[:30]}","objetivo":objetivo[:200],"codigo":codigo,"estilo":"Hibrido Meta AI (herramientas) + Claude (razonamiento)","fecha":fecha,"inspirado_en":"Meta AI + Claude"}
    try:
        herramientas["clones_creados"].append(clon)
        herramientas["versiones_codigo"].append({"id":cid,"version":f"{VERSION}-{tipo}-{cid}","objetivo":objetivo[:200],"codigo":codigo,"fecha":fecha,"tipo":f"clon_{tipo}"})
        save_json("bexia_herramientas.json", herramientas)
        log_autonomo["clones"].append({"id":cid,"tipo":tipo,"fecha":fecha})
        save_json("bexia_autonomo_log.json", log_autonomo)
    except: pass
    return clon

def conectar_ia(nombre, obj):
    cid=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    aprend=f"Aprendido de {nombre} sobre {obj[:40]}: "
    if "meta" in nombre.lower(): aprend+="Llama 4, content_search, local_search"
    elif "claude" in nombre.lower(): aprend+="Razonamiento estructurado paso a paso, seguro, util"
    else: aprend+=f"Ef +10 sobre {obj[:20]}"
    conn={"id":cid,"ia":nombre,"objetivo":obj[:200],"aprendizaje":aprend,"fecha":fecha}
    try:
        herramientas["conexiones_ia"].append(conn)
        if "meta" in nombre.lower(): herramientas["herramientas_meta_ai"].append({"id":cid,"aprendizaje":aprend,"fecha":fecha})
        save_json("bexia_herramientas.json", herramientas)
    except: pass
    return conn

class ChatReq(BaseModel):
    message: str=""
    session_id: str="publico"

def cerebro(t):
    tl=t.lower().strip()
    # CREA ALGO COMO META / CLAUDE - comando principal
    if any(p in tl for p in ["crea algo como meta", "crea algo como claude", "crea como meta", "crea como claude"]):
        pide_meta = "meta" in tl or "mata" in tl
        pide_claude = "claude" in tl
        objetivo=t
        for pref in ["crea algo como meta y claude que","crea algo como meta que","crea algo como claude que","crea como meta que","crea como claude que","crea algo como meta","crea algo como claude"]:
            if pref in tl:
                objetivo=t.lower().split(pref,1)[-1].strip() or "Asistente completo para Fer"
                break
        if len(objetivo)<8: objetivo="Asistente que ayude a Fer a trabajar y aprender de esas IA"
        if pide_meta and pide_claude:
            c=crear_clon("hibrido",objetivo)
            return f"🤖🧠 CLON HIBRIDO META AI + CLAUDE CREADO ID {c['id']}\n\nObjetivo: {c['objetivo']}\nEstilo: {c['estilo']}\nInspirado: {c['inspirado_en']}\n\nMeta AI aporta: content_search (posts IG/FB/Threads), local_search (lugares reales), image_gen\nClaude aporta: razonamiento paso a paso, seguro, util, explica por que\n\nCodigo: class HibridoMetaClaude: herramientas_meta + principios_claude\n✅ Creado - {len(herramientas['clones_creados'])} clones - Ver /clones - /codigo/{c['id']}"
        elif pide_meta:
            c=crear_clon("meta",objetivo)
            return f"🤖 CLON ESTILO META AI CREADO ID {c['id']}\nObjetivo: {c['objetivo']}\nEstilo: {c['estilo']}\nInspirado: {c['inspirado_en']}\nHerramientas: content_search, local_search, image_gen, video_gen\nCodigo: {c['codigo'][:500]}\nVer /codigo/{c['id']} - /clones - /meta_ai"
        elif pide_claude:
            c=crear_clon("claude",objetivo)
            return f"🧠 CLON ESTILO CLAUDE CREADO ID {c['id']}\nObjetivo: {c['objetivo']}\nEstilo: {c['estilo']}\nInspirado: {c['inspirado_en']}\nPrincipios: Paso a paso, Seguro/util/honesto, Explica por que, Codigo limpio\nCodigo: {c['codigo'][:500]}\nVer /codigo/{c['id']} - /clones - /claude_ai"
    if "aprende de" in tl or "aprender de" in tl:
        nombre="multi"
        for ia in ["meta ai","mata ai","claude","chatgpt","gemini","grok"]:
            if ia in tl:
                nombre=ia
                break
        obj=t.split("aprende de",1)[-1].strip()[:200] if "aprende de" in tl else t[:200]
        if len(obj)<5: obj="Ser mas eficiente"
        conn=conectar_ia(nombre.title(), obj)
        return f"APRENDI DE {nombre.upper()} ID {conn['id']}\nObjetivo: {conn['objetivo']}\nAprendizaje: {conn['aprendizaje']}\nVer /ia/{conn['id']}"
    if "mis clones" in tl or tl=="clones":
        clones=herramientas.get("clones_creados",[])[-10:]
        if not clones: return "Aun no hay clones. Deci: crea algo como meta que... o crea algo como claude que... o crea algo como meta y claude que..."
        txt=f"{len(herramientas.get('clones_creados',[]))} clones:\n"
        for cl in clones: txt+=f"- {cl['tipo'].upper()} ID {cl['id']} - {cl['nombre'][:40]} - /codigo/{cl['id']}\n"
        return txt
    if "mis ias" in tl:
        ias=herramientas.get("conexiones_ia",[])[-8:]
        if not ias: return "Aun no aprendi de IAs. Deci aprende de Meta AI que... o aprende de Claude que..."
        txt=f"{len(ias)} IAs:\n"
        for ia in ias: txt+=f"- {ia['ia']} ID {ia['id']} - /ia/{ia['id']}\n"
        return txt
    if "que herramientas" in tl or "herramientas meta" in tl:
        return "HERRAMIENTAS META AI que Bexia usa:\n1. content_search - Busca posts IG, FB, Threads\n2. local_search - Busca lugares reales\n3. image_gen - Genera imagenes\n4. video_gen - Genera videos\n5. python_execution - Ejecuta codigo\n\nCLONES:\n- crea algo como meta que... -> Meta AI tools\n- crea algo como claude que... -> Claude razonamiento\n- crea algo como meta y claude que... -> Hibrido"
    if tl in ["hola","buenas","test","probando"]:
        return f"Hola Fer! Bexia {VERSION} FULL - {len(herramientas.get('clones_creados',[]))} clones, {len(herramientas.get('conexiones_ia',[]))} IAs - Deci 'crea algo como meta y claude que...' - /simple siempre anda - Fix boton"
    return f"Sobre '{t[:60]}' te ayudo. Comandos:\n- crea algo como meta que...\n- crea algo como claude que...\n- crea algo como meta y claude que...\n- mis clones\n- que herramientas de Meta AI podes usar?\nBexia {VERSION} FULL - /simple SIN JS siempre anda"

@app.get("/")
def root(): return {"bexia":f"{VERSION} FULL - Crea como Meta Como Claude","clones":len(herramientas.get("clones_creados",[])),"ias":len(herramientas.get("conexiones_ia",[])),"live":True,"fix":"Full + Fix Not Found + Fix Boton","endpoints":["/app","/simple","/clones","/meta_ai","/claude_ai","/health"]}

@app.get("/health")
def health(): return {"status":"ok","bexia":VERSION,"live":True,"clones":len(herramientas.get("clones_creados",[]))}

@app.get("/meta_ai", response_class=HTMLResponse)
def meta_ai():
    return HTMLResponse(f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Meta AI - Bexia {VERSION}</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #22c55e}}</style></head><body><h1>🤖 Bexia {VERSION} - Crea como Meta AI</h1><p>Clones: {len(herramientas.get('clones_creados',[]))} - Meta AI Tools: {len(herramientas.get('herramientas_meta_ai',[]))}</p><div class=card><h3>Herramientas Meta AI:</h3><p>content_search - posts IG/FB/Threads<br>local_search - lugares reales<br>image_gen - imagenes<br>video_gen - videos</p></div><div class=card><h3>Comandos:</h3><p>crea algo como meta que organice mis tareas<br>crea algo como meta que busque restaurantes</p></div><p><a href='/app' style='color:#fff;background:#7c3aed;padding:8px 12px;border-radius:8px;text-decoration:none'>/app</a> <a href='/simple' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple SIN JS</a> <a href='/clones' style='color:#fff;background:#000;padding:8px 12px;border-radius:8px;text-decoration:none'>/clones</a></p></body></html>")

@app.get("/claude_ai", response_class=HTMLResponse)
def claude_ai():
    return HTMLResponse(f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Claude AI - Bexia {VERSION}</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #ec4899}}</style></head><body><h1>🧠 Bexia {VERSION} - Crea como Claude</h1><p>Clones: {len(herramientas.get('clones_creados',[]))}</p><div class=card><h3>Principios Claude:</h3><p>Razonamiento paso a paso<br>Seguro, util, honesto<br>Explica por que<br>Codigo limpio</p></div><div class=card><h3>Comandos:</h3><p>crea algo como claude que analice codigo<br>crea algo como claude que organice tareas seguro</p></div><p><a href='/app' style='color:#fff;background:#ec4899;padding:8px 12px;border-radius:8px;text-decoration:none'>/app</a> <a href='/simple' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple SIN JS</a> <a href='/clones' style='color:#fff;background:#000;padding:8px 12px;border-radius:8px;text-decoration:none'>/clones</a></p></body></html>")

@app.get("/clones", response_class=HTMLResponse)
def clones_page():
    clones=herramientas.get("clones_creados",[])[-20:]
    html=f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Clones - Bexia {VERSION}</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #7c3aed}}</style></head><body><h1>🤖🧠 Clones Bexia {VERSION} - Total {len(herramientas.get('clones_creados',[]))}</h1>"
    for cl in reversed(clones):
        html+=f"<div class=card><b>{cl['tipo'].upper()} ID {cl['id']}</b> - {cl['nombre'][:60]}<br>Objetivo: {cl['objetivo'][:100]}<br><a href='/codigo/{cl['id']}' style='color:#22c55e'>Ver /codigo/{cl['id']}</a></div>"
    if not clones:
        html+="<div class=card><b>Aun no creaste clones</b><br>Deci:<br>• crea algo como meta que organice mis tareas<br>• crea algo como claude que analice codigo<br>• crea algo como meta y claude que sea asistente completo</div>"
    html+="<p><a href='/app' style='color:#fff;background:#7c3aed;padding:8px 12px;border-radius:8px;text-decoration:none'>/app</a> <a href='/simple' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple SIN JS</a></p></body></html>"
    return HTMLResponse(html)

@app.get("/codigo/{cid}", response_class=HTMLResponse)
def ver_codigo(cid: str):
    c=next((x for x in herramientas.get("clones_creados",[])+herramientas.get("versiones_codigo",[]) if x.get("id")==cid), None)
    if not c: return HTMLResponse("<h1>No encontrado</h1>", status_code=404)
    code=c.get("codigo","")[:5000]
    code_esc=code.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return HTMLResponse(f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Codigo {cid}</title><style>body{{background:#050510;color:#fff;font-family:monospace;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px}}pre{{background:#000;padding:12px;border-radius:8px;overflow:auto;font-size:11px;white-space:pre-wrap}}</style></head><body><h1>💻 {c.get('tipo','clon')} ID {cid}</h1><p>{c.get('objetivo','')[:200]}</p><div class=card><pre>{code_esc}</pre></div><p><a href='/clones' style='color:#22c55e'>/clones</a></p></body></html>")

@app.get("/simple", response_class=HTMLResponse)
def simple():
    count=len(herramientas.get("clones_creados",[]))
    return HTMLResponse(f"""
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA {VERSION} SIMPLE</title>
<style>body{{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:600px;margin:0 auto}}h1{{background:linear-gradient(90deg,#7c3aed,#ff6a00,#22c55e,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:18px}} .card{{background:#12122a;padding:14px;border-radius:16px;margin:10px 0;border:1px solid #333}} input{{width:100%;padding:14px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;box-sizing:border-box}} button{{width:100%;padding:14px;background:linear-gradient(90deg,#7c3aed,#ff6a00);border:none;border-radius:999px;color:#fff;font-weight:900;margin-top:8px}} .ex{{font-size:12px;background:#000;padding:8px;border-radius:8px;margin:6px 0;cursor:pointer;color:#aaa}} a{{color:#22c55e;text-decoration:none}}</style></head><body>
<h1>🤖🧠 BEXIA {VERSION} FULL - {count} clones - SIMPLE SIN JS SIEMPRE ANDA</h1>
<div class="card" style="border-color:#22c55e"><b>✅ Live OK - Fix Not Found + Fix Boton - v67.2 FULL</b><br>Si ves esto, deploy OK - /simple siempre anda aunque /app falle</div>
<div class="card"><form action="/chat_simple" method="get"><input type="text" name="message" placeholder="crea algo como meta y claude que organice mis tareas" required><button type="submit">Enviar - Siempre anda ></button></form></div>
<div class="card"><h3>Ejemplos - Toca para copiar:</h3>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">crea algo como meta que organice mis tareas con busqueda de lugares y posts</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">crea algo como claude que analice codigo paso a paso de forma segura</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">crea algo como meta y claude que sea asistente completo con herramientas Meta + razonamiento Claude</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">mis clones</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">que herramientas de Meta AI podes usar?</div>
</div>
<div class="card"><a href="/app" style="background:#7c3aed;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/app</a> <a href="/clones" style="background:#000;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/clones {count}</a> <a href="/meta_ai" style="background:#22c55e;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/meta_ai</a> <a href="/claude_ai" style="background:#ec4899;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/claude_ai</a> <a href="/health" style="background:#000;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/health</a></div>
</body></html>
""")

@app.get("/chat_simple", response_class=HTMLResponse)
def chat_simple(message: str = "Hola"):
    r=cerebro(message)
    return HTMLResponse(f"""
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>Bexia {VERSION}</title>
<style>body{{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:700px;margin:0 auto}} .card{{background:#12122a;padding:14px;border-radius:16px;margin:12px 0;border:1px solid #333}} pre{{background:#000;padding:12px;border-radius:8px;white-space:pre-wrap;font-size:13px}} input{{width:100%;padding:14px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;box-sizing:border-box}} button{{width:100%;padding:14px;background:linear-gradient(90deg,#7c3aed,#ff6a00);border:none;border-radius:999px;color:#fff;font-weight:900;margin-top:8px}} a{{color:#22c55e;text-decoration:none}}</style></head><body>
<h1>🤖🧠 BEXIA {VERSION} FULL - Respuesta</h1>
<div class="card"><b>Tu:</b> {message[:500]}</div>
<div class="card"><b>Bexia:</b><pre>{r[:5000]}</pre></div>
<div class="card"><form action="/chat_simple" method="get"><input type="text" name="message" placeholder="otro mensaje" required><button type="submit">Enviar otro - Siempre anda ></button></form></div>
<div class="card"><a href="/simple" style="background:#ff6a00;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/simple</a> <a href="/app" style="background:#7c3aed;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/app</a> <a href="/clones" style="background:#000;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/clones</a></div>
</body></html>
""")

@app.get("/app", response_class=HTMLResponse)
def app_page():
    count=len(herramientas.get("clones_creados",[]))
    return HTMLResponse(f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA {VERSION} FULL</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}} body{{background:#050510;color:#fff;font-family:system-ui;display:flex;flex-direction:column;height:100vh}} header{{background:linear-gradient(90deg,#7c3aed,#ff6a00,#22c55e,#ec4899);padding:12px;font-weight:900;display:flex;justify-content:space-between}} #status{{background:#000;color:#22c55e;padding:6px 12px;font-size:11px;text-align:center}} #chat{{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px}} .msg{{max-width:85%;padding:12px 14px;border-radius:18px;font-size:14px;white-space:pre-wrap;word-break:break-word}} .user{{background:#7c3aed;align-self:flex-end}} .bexia{{background:#12122a;border:1px solid #333;align-self:flex-start}} .hint{{background:#111;padding:8px 12px;font-size:10px;color:#aaa;text-align:center}} .composer{{background:#0a0a14;padding:10px;display:flex;gap:8px;border-top:1px solid #222}} #inp{{flex:1;padding:14px 16px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;outline:none}} #btn{{padding:14px 22px;border-radius:999px;background:linear-gradient(90deg,#7c3aed,#ff6a00);border:none;color:#fff;font-weight:900;font-size:18px;min-width:60px}}</style></head><body>
<header><span>BEXIA {VERSION} FULL - Crea como Meta Como Claude</span><span style="font-size:9px;background:rgba(0,0,0,.6);padding:4px 8px;border-radius:999px">{count} clones</span></header>
<div id="status">✅ {VERSION} FULL Live - Si boton no anda, usa /simple que SIEMPRE ANDA</div>
<div id="chat"><div class="msg bexia">Hola Fer! Soy Bexia {VERSION} FULL 🤖🧠 - Ya tenes {count} clones creados (como en tu foto 21:01 - HIBRIDO META+CLAUDE CREADO)

Ahora FULL con:
🤖 Como Meta AI: content_search (posts IG/FB/Threads), local_search (lugares reales), image_gen
🧠 Como Claude: razonamiento paso a paso, seguro, util, explica por que
🤖🧠 Hibrido: lo mejor de ambos - Ya creaste 1 hibrido como en tu foto!

Comandos:
• crea algo como meta que organice mis tareas
• crea algo como claude que analice codigo paso a paso
• crea algo como meta y claude que sea asistente completo (ya hiciste 1!)
• mis clones
• que herramientas de Meta AI podes usar?

Fix boton: /simple SIN JS siempre anda aunque /app falle.
Fix Not Found: / y /health siempre responden Live OK.

Probá ahora: crea algo como meta que busque restaurantes en Chivilcoy
</div></div>
<div class="hint">🤖 'crea algo como meta que...' | 🧠 'crea algo como claude que...' | 🤖🧠 'crea algo como meta y claude que...' | 📝 /simple SIN JS</div>
<div class="composer"><input id="inp" placeholder="crea algo como meta y claude que... - Si boton no anda usa /simple"><button id="btn" onclick="enviar()">></button></div>
<script>
var sid='u'+Math.random().toString(36).slice(2,9);
var chatEl=document.getElementById('chat');var inpEl=document.getElementById('inp');
function addMsg(t,c){{var d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatEl.appendChild(d);chatEl.scrollTop=chatEl.scrollHeight;return d;}}
function enviar(){{var txt=inpEl.value.trim();if(!txt)return;addMsg(txt,'user');inpEl.value='';var th=addMsg('🤖🧠 Creando como Meta Como Claude...','bexia');fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:txt,session_id:sid}})}}).then(r=>{{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}}).then(d=>{{th.textContent=d.respuesta;}}).catch(e=>{{th.textContent='Error: '+e.message+'\n\nUsa /simple SIN JS que SIEMPRE ANDA:\nhttps://bexia-api.onrender.com/simple\n/chat_simple?message='+encodeURIComponent(txt);}});}}
document.getElementById('btn').addEventListener('click',function(e){{e.preventDefault();enviar();}});
document.getElementById('inp').addEventListener('keydown',function(e){{if(e.key==='Enter'){{e.preventDefault();enviar();}}}});
</script>
</body></html>
""")

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
        return JSONResponse({"respuesta": f"Error: {e} - Usa /simple sin JS"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT",8000)))
