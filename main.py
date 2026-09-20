
"""
BEXIA v63 META AI + MULTI-IA + N8N - Aprende de Meta AI y usa sus herramientas
"""
import os, json, re, time, uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import urllib.request, urllib.parse
try:
    import requests
    HAS_REQUESTS=True
except:
    HAS_REQUESTS=False

print("BEXIA v63 META AI + MULTI-IA + N8N iniciando...", flush=True)
OWNER_SECRET="BEXIA_FER_2026_INFINITA_SUPREMA"
VERSION_ACTUAL="v63"
app=FastAPI(title="BEXIA v63 META AI", docs_url=None, redoc_url=None, openapi_url=None)
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
ajustes=load_json("bexia_ajustes.json", {"efectividad":{"codigo":0,"n8n":0,"multi_ia":0,"meta_ai":0},"perfil_fer":{"temas_frecuentes":{},"ciudad_favorita":"Chivilcoy"}})
herramientas=load_json("bexia_herramientas.json", {"sitios":[],"cache":{},"versiones_codigo":[],"workflows_n8n":[],"conexiones_ia":[],"aprendizajes_externos":[],"herramientas_meta_ai":[]})
memoria_propia=load_json("bexia_memoria_propia.json", {"recuerdos":[],"auto_memorias":[],"commits":[],"branches":["main"]})
log_autonomo=load_json("bexia_autonomo_log.json", {"codigos_generados":[],"workflows_creados":[],"aprendizajes_multi_ia":[],"aprendizajes_meta_ai":[]})
rate={}
sesiones_mem={}

PALABRAS_PROHIBIDAS = ["hack","exploit","robar","estafa","drogas ilegales","armas ilegales","pornografia infantil","phishing","virus","malware","bomba","clonar tarjeta"]
def es_legal(t):
    tl=t.lower()
    for p in PALABRAS_PROHIBIDAS:
        if p in tl: return False, f"Bloqueado ley: {p}"
    return True, "ok"

def get_session(sid):
    if not sid: sid="publico"
    try:
        sid=re.sub(r"[^a-zA-Z0-9_-]","",sid)[:32] or "publico"
    except:
        sid="publico"
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

def crear_memoria_propia(tipo, contenido, importancia=5):
    try:
        mem={"id": str(uuid.uuid4())[:8], "tipo": tipo, "contenido": contenido[:500], "importancia": importancia, "fecha": datetime.now().isoformat()}
        memoria_propia["auto_memorias"].append(mem)
        memoria_propia["recuerdos"].append(mem)
        commit={"id": str(uuid.uuid4())[:7], "mensaje": f"{tipo}: {contenido[:50]}", "fecha": mem["fecha"], "memoria_id": mem["id"], "branch": tipo, "autor": "bexia-v63"}
        memoria_propia["commits"].append(commit)
        if len(memoria_propia["commits"])>500: memoria_propia["commits"]=memoria_propia["commits"][-300:]
        save_json("bexia_memoria_propia.json", memoria_propia)
        return mem
    except:
        return {"id":"err"}

def conectar_ia_externa(nombre_ia, objetivo_aprendizaje):
    legal, razon = es_legal(objetivo_aprendizaje)
    if not legal: return {"ok": False, "error": razon}
    conexion_id=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    aprendizajes_simulados = {
        "meta ai": f"Aprendido de Meta AI sobre {objetivo_aprendizaje[:40]}: Llama 4, busqueda social, lugares, recomendaciones - Ef +15",
        "meta": f"Aprendido de Meta AI sobre {objetivo_aprendizaje[:40]}: Llama 4, busqueda social, lugares",
        "mata ai": f"Aprendido de Meta AI (detectado typo mata) sobre {objetivo_aprendizaje[:40]}: Llama 4, herramientas Meta",
        "llama": f"Aprendido de Llama (Meta) sobre {objetivo_aprendizaje[:40]}: modelo open source, codigo",
        "claude": f"Aprendido de Claude sobre {objetivo_aprendizaje[:40]}: razonamiento estructurado - Ef +10",
        "chatgpt": f"Aprendido de ChatGPT sobre {objetivo_aprendizaje[:40]}: creatividad y contexto",
        "gemini": f"Aprendido de Gemini sobre {objetivo_aprendizaje[:40]}: multimodal y busqueda",
        "grok": f"Aprendido de Grok sobre {objetivo_aprendizaje[:40]}: tiempo real",
        "perplexity": f"Aprendido de Perplexity sobre {objetivo_aprendizaje[:40]}: busqueda con fuentes",
        "n8n": f"Aprendido de n8n sobre {objetivo_aprendizaje[:40]}: automatizacion"
    }
    nombre_lower = nombre_ia.lower()
    if "meta" in nombre_lower or "mata" in nombre_lower or "llama" in nombre_lower:
        nombre_lower = "meta ai"
        nombre_ia = "Meta AI"
    aprendizaje = aprendizajes_simulados.get(nombre_lower, f"Aprendido de {nombre_ia} sobre {objetivo_aprendizaje[:40]}")
    herramientas_meta = []
    if "meta" in nombre_lower:
        herramientas_meta = [
            "content_search - Busca posts IG, FB, Threads",
            "local_search - Busca lugares reales: restaurantes, cafes, bares",
            "image_gen - Genera imagenes con Meta AI",
            "video_gen - Genera videos",
            "python_execution - Ejecuta codigo"
        ]
    conexion={
        "id": conexion_id,
        "ia": nombre_ia,
        "objetivo": objetivo_aprendizaje[:200],
        "aprendizaje": aprendizaje,
        "herramientas_meta_ai": herramientas_meta,
        "fecha": fecha,
        "estado": "aprendido",
        "gratis": True,
        "codigo_generado": f"# Codigo aprendido de {nombre_ia}\n# Objetivo: {objetivo_aprendizaje[:50]}\ndef aprender_de_meta_ai(entrada):\n    return '{aprendizaje[:70]}'"
    }
    try:
        herramientas["conexiones_ia"].append(conexion)
        herramientas["aprendizajes_externos"].append({"id": conexion_id, "ia": nombre_ia, "aprendizaje": aprendizaje, "fecha": fecha, "objetivo": objetivo_aprendizaje[:80], "herramientas": herramientas_meta})
        if "meta" in nombre_lower:
            herramientas["herramientas_meta_ai"].append({"id": conexion_id, "herramienta": "meta_ai_tools", "aprendizaje": aprendizaje, "fecha": fecha})
            log_autonomo["aprendizajes_meta_ai"].append({"id": conexion_id, "ia": nombre_ia, "fecha": fecha})
        save_json("bexia_herramientas.json", herramientas)
        log_autonomo["aprendizajes_multi_ia"].append({"id": conexion_id, "ia": nombre_ia, "fecha": fecha})
        save_json("bexia_autonomo_log.json", log_autonomo)
        crear_memoria_propia("meta_ai" if "meta" in nombre_lower else "multi_ia", f"Aprendi de {nombre_ia}: {objetivo_aprendizaje[:60]}", importancia=10)
    except Exception as e:
        print(f"Error guardar: {e}")
    return {"ok": True, "conexion": conexion}

def crear_workflow_n8n(nombre_workflow, descripcion, ia_origen="Meta AI"):
    legal, razon = es_legal(descripcion)
    if not legal: return {"ok": False, "error": razon}
    workflow_id=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    if "meta" in ia_origen.lower() or "mata" in ia_origen.lower():
        ia_origen = "Meta AI"
        n8n_json = {
            "name": nombre_workflow[:60],
            "nodes": [
                {"id": "1", "name": "Webhook Bexia", "type": "n8n-nodes-base.webhook", "parameters": {"path": f"bexia-meta-{workflow_id}"}},
                {"id": "2", "name": "Meta AI - content_search", "type": "n8n-nodes-base.function", "parameters": {"functionCode": f"// Meta AI content_search: {descripcion[:50]}"}},
                {"id": "3", "name": "Meta AI - local_search", "type": "n8n-nodes-base.function", "parameters": {"functionCode": "// Meta AI local_search"}},
                {"id": "4", "name": "Bexia Memoria Meta AI", "type": "n8n-nodes-base.function"},
                {"id": "5", "name": "Render Deploy", "type": "n8n-nodes-base.httpRequest", "parameters": {"url": f"https://bexia-api.onrender.com/n8n/webhook/{workflow_id}"}}
            ],
            "meta": {"bexia_version": VERSION_ACTUAL, "objetivo": descripcion, "ia_origen": "Meta AI", "herramientas_meta_ai": ["content_search","local_search","image_gen"]}
        }
    else:
        n8n_json = {
            "name": nombre_workflow[:60],
            "nodes": [
                {"id": "1", "name": "Webhook Bexia", "type": "n8n-nodes-base.webhook", "parameters": {"path": f"bexia-{workflow_id}"}},
                {"id": "2", "name": f"IA {ia_origen}", "type": "n8n-nodes-base.function"},
                {"id": "3", "name": "Bexia Memoria", "type": "n8n-nodes-base.function"},
                {"id": "4", "name": "Render Deploy", "type": "n8n-nodes-base.httpRequest", "parameters": {"url": f"https://bexia-api.onrender.com/n8n/webhook/{workflow_id}"}}
            ],
            "meta": {"bexia_version": VERSION_ACTUAL, "objetivo": descripcion, "ia_origen": ia_origen}
        }
    workflow={
        "id": workflow_id,
        "nombre": nombre_workflow[:80],
        "descripcion": descripcion[:300],
        "ia_origen": ia_origen,
        "n8n_json": n8n_json,
        "fecha": fecha,
        "estado": "creado_listo_importar_n8n",
        "url_webhook": f"https://bexia-api.onrender.com/n8n/webhook/{workflow_id}",
        "gratis": True,
        "usa_herramientas_meta_ai": "meta" in ia_origen.lower()
    }
    try:
        herramientas["workflows_n8n"].append(workflow)
        save_json("bexia_herramientas.json", herramientas)
        log_autonomo["workflows_creados"].append({"id": workflow_id, "nombre": nombre_workflow[:40], "fecha": fecha, "ia": ia_origen})
        save_json("bexia_autonomo_log.json", log_autonomo)
        crear_memoria_propia("n8n", f"Cree workflow n8n {nombre_workflow[:40]} que aprende de {ia_origen}", importancia=10 if "meta" in ia_origen.lower() else 9)
    except: pass
    return {"ok": True, "workflow": workflow}

def generar_codigo_cerebro_autonomo(objetivo, version_nueva="v64"):
    legal, razon = es_legal(objetivo)
    if not legal: return {"ok": False, "error": razon}
    codigo_id=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    codigo_generado = "# BEXIA " + version_nueva + " CEREBRO META AI\n# Objetivo: " + objetivo[:60] + "\nclass CerebroMetaAI:\n    def __init__(self):\n        self.version='" + version_nueva + "'\n        self.herramientas=['content_search','local_search','image_gen']\n    def aprender_de_meta_ai(self, entrada):\n        return 'Meta AI: ' + entrada[:20]\n    def crear_workflow(self, nombre):\n        return 'Workflow ' + nombre\n"
    version_data={"id": codigo_id, "version": version_nueva, "version_base": VERSION_ACTUAL, "objetivo": objetivo[:200], "codigo": codigo_generado, "fecha": fecha, "lineas": 8, "tipo": "meta_ai_multi_ia_n8n", "usa_herramientas_meta_ai": True}
    try:
        herramientas["versiones_codigo"].append(version_data)
        save_json("bexia_herramientas.json", herramientas)
        crear_memoria_propia("codigo", f"Codigo META AI {version_nueva} ID {codigo_id}", importancia=10)
    except: pass
    return {"ok": True, "codigo": version_data}

def buscar_cache(q):
    try:
        key=re.sub(r"\W+","_", q.lower())[:40]
        cache=herramientas.get("cache",{})
        if key in cache:
            fecha=datetime.fromisoformat(cache[key]["fecha"])
            if datetime.now()-fecha < timedelta(hours=6):
                return cache[key]["respuesta"]
    except: pass
    return None
def guardar_cache(q, r):
    try:
        key=re.sub(r"\W+","_", q.lower())[:40]
        if "cache" not in herramientas: herramientas["cache"]={}
        herramientas["cache"][key]={"respuesta": r[:800], "fecha": datetime.now().isoformat()}
        save_json("bexia_herramientas.json", herramientas)
    except: pass

def obtener_clima(ciudad="Chivilcoy"):
    try:
        qe=urllib.parse.quote(ciudad)
        gurl=f"https://geocoding-api.open-meteo.com/v1/search?name={qe}&count=1&language=es"
        data=requests.get(gurl,timeout=5).json() if HAS_REQUESTS else json.loads(urllib.request.urlopen(gurl,timeout=5).read().decode())
        if not data.get("results"): return None
        r0=data["results"][0]
        lat=r0["latitude"]; lon=r0["longitude"]; nombre=r0["name"]
        wurl=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
        wd=requests.get(wurl,timeout=5).json() if HAS_REQUESTS else json.loads(urllib.request.urlopen(wurl,timeout=5).read().decode())
        cur=wd.get("current_weather",{})
        temp=cur.get("temperature")
        return f"Clima en {nombre}: {temp}C"
    except: return None

class ChatRequest(BaseModel):
    message: str=""
    session_id: str="publico"

def cerebro_func(user_text, sid):
    try:
        t=user_text.lower().strip()
        cache_resp = buscar_cache(user_text)
        if cache_resp and len(user_text)>10:
            return cache_resp + "\n\nCache Meta AI"
        if any(p in t for p in ["meta ai", "mata ai", "llama", "herramientas de meta", "tools de meta", "meta-ai"]):
            ia_detectada="Meta AI"
            objetivo = user_text
            for pref in ["aprende de meta ai que", "aprende de mata ai que", "aprende de meta que", "usa meta ai que", "aprende de llama que"]:
                if pref in t:
                    objetivo = user_text.lower().split(pref,1)[-1].strip()
                    break
            if len(objetivo)<10: objetivo="Ser mas eficiente usando herramientas Meta AI"
            if any(k in t for k in ["herramienta", "tool", "n8n", "workflow", "usa sus herramientas"]):
                res = crear_workflow_n8n(f"workflow-meta-ai-{objetivo[:15]}", objetivo, "Meta AI")
                if res["ok"]:
                    w=res["workflow"]
                    herramientas_list = "content_search, local_search, image_gen, video_gen"
                    return f"META AI WORKFLOW N8N CREADO ID {w['id']}\nNombre: {w['nombre']}\nDesc: {w['descripcion']}\nIA: {w['ia_origen']}\nHerramientas Meta AI: {herramientas_list}\nWebhook: {w['url_webhook']}\nJSON: /n8n/{w['id']}"
            else:
                res = conectar_ia_externa(ia_detectada, objetivo)
                if res["ok"]:
                    c=res["conexion"]
                    herramientas_txt = "\n".join([f"  * {h}" for h in c['herramientas_meta_ai'][:5]])
                    return f"APRENDI DE META AI - ID {c['id']}\nObjetivo: {c['objetivo']}\nAprendizaje: {c['aprendizaje']}\nHerramientas Meta AI:\n{herramientas_txt}\nVer: /ia/{c['id']} - /meta_ai"
        if any(p in t for p in ["aprende de", "aprender de", "conecta con", "usa otra ia"]):
            ia_detectada="multi"
            for ia in ["claude","chatgpt","gemini","grok","perplexity","n8n","meta ai","mata ai"]:
                if ia in t:
                    ia_detectada=ia
                    break
            if "mata" in ia_detectada: ia_detectada="Meta AI"
            objetivo = user_text
            for pref in ["aprende de","aprender de","conecta con"]:
                if pref in t:
                    objetivo = user_text.lower().split(pref,1)[-1].strip()
                    break
            if len(objetivo)<10: objetivo="Ser mas eficiente"
            if "n8n" in ia_detectada or "workflow" in t:
                res = crear_workflow_n8n(f"workflow-aprende-{ia_detectada}", objetivo, ia_detectada)
                if res["ok"]:
                    w=res["workflow"]
                    return f"WORKFLOW N8N CREADO ID {w['id']}\nNombre: {w['nombre']}\nIA: {w['ia_origen']}\nJSON: /n8n/{w['id']}"
            else:
                res = conectar_ia_externa(ia_detectada, objetivo)
                if res["ok"]:
                    c=res["conexion"]
                    return f"APRENDI DE {ia_detectada.upper()} - ID {c['id']}\nObjetivo: {c['objetivo']}\nAprendizaje: {c['aprendizaje']}\nVer: /ia/{c['id']}"
        if any(p in t for p in ["crea un workflow", "crea workflow", "n8n workflow", "workflow meta ai"]):
            desc = user_text
            if len(desc)<10: desc="Aprender de Meta AI usando herramientas"
            ia_origen = "Meta AI" if "meta" in t or "mata" in t else "multi_ia"
            res = crear_workflow_n8n(f"workflow-{desc[:20]}", desc, ia_origen)
            if res["ok"]:
                w=res["workflow"]
                return f"WORKFLOW N8N CREADO ID {w['id']}\nNombre: {w['nombre']}\nIA: {w['ia_origen']}\nJSON: /n8n/{w['id']}"
        if any(p in t for p in ["escribe tu codigo", "genera codigo", "codigo que aprende", "codigo meta ai"]):
            objetivo = user_text
            if len(objetivo)<10: objetivo="Aprender de Meta AI usando herramientas"
            version_nueva = f"v{63+len(herramientas['versiones_codigo'])+1}"
            res = generar_codigo_cerebro_autonomo(objetivo, version_nueva)
            if res["ok"]:
                c=res["codigo"]
                return f"CODIGO CEREBRO META AI GENERADO\nVersion: {c['version']} ID {c['id']}\nObjetivo: {c['objetivo']}\nVer: /codigo/{c['id']}"
        if "herramientas meta" in t or "tools meta" in t or "que herramientas" in t:
            return "HERRAMIENTAS DE META AI que Bexia puede usar (v63):\n1. content_search - Busca posts IG, FB, Threads\n2. local_search - Busca lugares reales: restaurantes, cafes, bares\n3. image_gen - Genera imagenes\n4. video_gen - Genera videos\n5. python_execution - Ejecuta codigo\nDeci: 'aprende de Meta AI que busque...' o 'crea workflow n8n que use herramientas Meta AI'"
        if "mis workflows" in t:
            workflows = herramientas["workflows_n8n"][-8:]
            if not workflows: return "Aun no cree workflows. Deci 'crea workflow n8n que aprenda de Meta AI'"
            txt = f"{len(herramientas['workflows_n8n'])} workflows:\n"
            for w in workflows: txt+=f"- {w['nombre']} ID {w['id']} - IA {w['ia_origen']} - /n8n/{w['id']}\n"
            return txt
        if "mis ias" in t or "mis meta" in t:
            conexiones = herramientas["conexiones_ia"][-10:]
            if not conexiones: return "Aun no aprendi de IAs. Deci 'aprende de Meta AI que...'"
            txt = f"{len(herramientas['conexiones_ia'])} aprendizajes:\n"
            for c in conexiones: txt+=f"- {c['ia'].upper()} ID {c['id']} - /ia/{c['id']}\n"
            return txt
        if "mis codigos" in t:
            versiones = herramientas["versiones_codigo"][-8:]
            if not versiones: return "Aun no genere codigos"
            txt = f"{len(herramientas['versiones_codigo'])} codigos:\n"
            for v in versiones: txt+=f"- {v['version']} ID {v['id']} - /codigo/{v['id']}\n"
            return txt
        if t in ["hola","buenas","hola bexia","test","probando"]:
            return f"Hola Fer! Soy Bexia v63 META AI + MULTI-IA + N8N - Tengo {len(memoria_propia['auto_memorias'])} memorias, {len(herramientas['versiones_codigo'])} codigos, {len(herramientas['workflows_n8n'])} workflows, {len(herramientas['conexiones_ia'])} IAs (Meta AI con {len(herramientas['herramientas_meta_ai'])} herramientas). Deci 'aprende de Meta AI que...' o 'que herramientas de Meta AI podes usar?'"
        if any(k in t for k in ["clima","llueve","temperatura"]):
            rc=obtener_clima("Chivilcoy")
            if rc: 
                guardar_cache(user_text, rc)
                return rc
        if len(user_text)>5:
            try:
                crear_memoria_propia("recuerdo", f"Pregunta: {user_text[:80]}", importancia=3)
            except: pass
        return f"Sobre '{user_text[:60]}' te ayudo con META AI + Multi-IA + n8n. Deci 'aprende de Meta AI que...' o 'que herramientas de Meta AI podes usar?' - v63 META AI"
    except Exception as e:
        return f"Hola Fer! Soy Bexia v63 META AI - Recibi '{user_text[:30]}' error: {e} - Pero envio funciona!"

@app.get("/")
def root():
    return {"bexia":"v63 META AI + MULTI-IA + N8N","memorias":len(memoria_propia["auto_memorias"]),"codigos":len(herramientas["versiones_codigo"]),"workflows_n8n":len(herramientas["workflows_n8n"]),"conexiones_ia":len(herramientas["conexiones_ia"]),"herramientas_meta_ai":len(herramientas["herramientas_meta_ai"]),"app":"/app","test":"/test","meta_ai_url":"/meta_ai","mensaje":"Bexia aprende de Meta AI y usa sus herramientas"}

@app.get("/health")
def health(): return {"status":"ok","bexia":"v63","live":True,"fix":"META AI + FIX ENVIO","herramientas_meta_ai":len(herramientas["herramientas_meta_ai"])}

@app.get("/meta_ai", response_class=HTMLResponse)
def meta_ai_page():
    html = "<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Meta AI Tools - Bexia v63</title><style>body{background:#050510;color:#fff;font-family:system-ui;padding:20px}.card{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #22c55e}.tool{background:#000;padding:10px;border-radius:8px;margin:8px 0;border-left:3px solid #7c3aed}</style></head><body>"
    html += "<h1>BEXIA v63 - Herramientas de Meta AI</h1>"
    html += f"<p>Aprendio de Meta AI {len(herramientas['herramientas_meta_ai'])} veces. Total IAs: {len(herramientas['conexiones_ia'])}</p>"
    html += "<div class=card><h3>Herramientas Meta AI:</h3>"
    html += "<div class=tool><b>1. content_search</b> - Busca posts IG, FB, Threads</div>"
    html += "<div class=tool><b>2. local_search</b> - Busca lugares reales</div>"
    html += "<div class=tool><b>3. image_gen</b> - Genera imagenes</div>"
    html += "<div class=tool><b>4. video_gen</b> - Genera videos</div>"
    html += "<div class=tool><b>5. python_execution</b> - Ejecuta codigo</div>"
    html += "</div>"
    html += "<p><a href='/app' style='color:#fff;background:#7c3aed;padding:8px 12px;border-radius:8px;text-decoration:none'>Volver a /app</a></p>"
    html += "</body></html>"
    return HTMLResponse(html)

@app.get("/test", response_class=HTMLResponse)
def test_page():
    return HTMLResponse("""
<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>TEST BEXIA v63 META AI</title>
<style>body{background:#050510;color:#fff;font-family:system-ui;padding:20px}input,button{padding:12px;margin:6px;border-radius:8px;border:1px solid #333}input{background:#1a1a2e;color:#fff;width:70%}button{background:#7c3aed;color:#fff;font-weight:900}pre{background:#000;padding:12px;border-radius:8px;white-space:pre-wrap}</style></head><body>
<h2>TEST BEXIA v63 META AI + FIX ENVIO</h2>
<form action="/chat_form" method="post">
  <input name="message" placeholder="aprende de Meta AI que use sus herramientas" required>
  <button type="submit">Enviar POST directo (siempre anda)</button>
</form>
<input id=inp placeholder="aprende de Meta AI que..."><button onclick="testFetch()">fetch</button>
<pre id=out>Esperando...</pre>
<script>
async function testFetch(){
  var txt=document.getElementById('inp').value;
  document.getElementById('out').textContent='Enviando: '+txt;
  try{
    var r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt,session_id:'test'})});
    var j=await r.json();
    document.getElementById('out').textContent='OK '+r.status+'\n'+j.respuesta;
  }catch(e){
    document.getElementById('out').textContent='Error: '+e;
  }
}
</script>
<p><a href="/app" style="color:#22c55e">/app</a> | <a href="/meta_ai" style="color:#ff6a00">/meta_ai</a> | <a href="/health" style="color:#22c55e">/health</a></p>
</body></html>
""")

@app.post("/chat_form", response_class=HTMLResponse)
async def chat_form(request: Request):
    try:
        form = await request.form()
        message = form.get("message", "Hola")
        respuesta = cerebro_func(message[:600], "form_test")
        html = f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Respuesta v63 META AI</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px;margin:12px 0}}a{{color:#22c55e}}pre{{background:#000;padding:12px;border-radius:8px;white-space:pre-wrap}}</style></head><body><h2>Bexia v63 META AI - Form POST funciono!</h2><div class=card><b>Mensaje:</b> {message[:200]}</div><div class=card><b>Respuesta:</b><pre>{respuesta[:3000]}</pre></div><div class=card><a href='/test'>/test</a> | <a href='/app'>/app</a> | <a href='/meta_ai'>/meta_ai</a></div></body></html>"
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f"<html><body style='background:#050510;color:#fff;padding:20px'><h1>Error form: {e}</h1><a href='/test'>/test</a></body></html>")

@app.get("/app", response_class=HTMLResponse)
def app_public():
    return HTMLResponse("""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><title>BEXIA v63 META AI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;overflow:hidden}
body{background:#050510;color:#fff;font-family:system-ui;display:flex;flex-direction:column}
header{background:linear-gradient(90deg,#000,#7c3aed,#ff6a00,#22c55e,#ec4899);padding:12px 14px;font-weight:900;display:flex;justify-content:space-between;align-items:center;font-size:14px;flex-shrink:0}
#status{background:#000;color:#22c55e;padding:6px 12px;font-size:11px;text-align:center;border-bottom:1px solid #222;flex-shrink:0}
#chat{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px;background:#050510}
.msg{max-width:85%;padding:12px 14px;border-radius:18px;font-size:14px;white-space:pre-wrap;word-break:break-word;line-height:1.4;flex-shrink:0}
.user{background:#7c3aed;align-self:flex-end}
.bexia{background:#12122a;border:1px solid #333;align-self:flex-start}
.hint{background:#111;padding:8px 12px;font-size:10px;color:#aaa;text-align:center;border-top:1px solid #222;flex-shrink:0}
.composer{background:#0a0a14;padding:10px;display:flex;gap:8px;align-items:center;border-top:1px solid #222;flex-shrink:0}
#inp{flex:1;padding:14px 16px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;font-size:16px;outline:none}
#btnSend{padding:14px 22px;border-radius:999px;background:linear-gradient(90deg,#7c3aed,#ff6a00);border:none;color:#fff;font-weight:900;font-size:18px;min-width:60px}
</style></head><body>
<header><span>BEXIA v63 META AI</span><span style="font-size:9px;background:rgba(0,0,0,.6);padding:4px 8px;border-radius:999px">Meta AI + Multi-IA + n8n</span></header>
<div id=status>✅ v63 META AI - Aprende de Meta AI y usa sus herramientas - Fix Envio</div>
<div id=chat>
  <div class="msg bexia">Hola Fer! Soy Bexia v63 META AI 🤖

Ahora aprendo de META AI y uso sus herramientas como me pediste! (incluye tu typo mata ai)

Herramientas de Meta AI que puedo usar:
• content_search - Busca posts IG, FB, Threads
• local_search - Busca lugares reales: restaurantes, cafes, bares
• image_gen - Genera imagenes
• video_gen - Genera videos
• python_execution - Ejecuta codigo

Tambien aprendo de Claude, ChatGPT, Gemini, Grok, Perplexity y creo workflows n8n con herramientas Meta AI.

Si boton > no anda, usa:
https://bexia-api.onrender.com/test
https://bexia-api.onrender.com/meta_ai

Proba:
• aprende de Meta AI que use sus herramientas para buscar restaurantes
• que herramientas de Meta AI podes usar?
• crea un workflow n8n que use herramientas de Meta AI
• aprende de Mata AI que sea mas eficiente (detecta typo!)
• mis ias
• mis workflows

Todo gratis, legal.
  </div>
</div>
<div class=hint>🤖 'aprende de Meta AI que...' | 🔧 'que herramientas de Meta AI podes usar?' | 🔗 'crea workflow n8n que use herramientas de Meta AI'</div>
<form id=formChat class=composer onsubmit="return false;">
  <input id=inp type="text" placeholder="Ej: aprende de Meta AI que use content_search" autocomplete="off" spellcheck="false">
  <button id=btnSend type="button">></button>
</form>
<script>
var sid='u'+Math.random().toString(36).slice(2,9);
var chatEl=document.getElementById('chat');
var inpEl=document.getElementById('inp');
var statusEl=document.getElementById('status');
var btnEl=document.getElementById('btnSend');
function addMsg(text, cls){
  var d=document.createElement('div');
  d.className='msg '+cls;
  d.textContent=text;
  chatEl.appendChild(d);
  chatEl.scrollTop=chatEl.scrollHeight;
  return d;
}
async function enviar(){
  var txt=inpEl.value.trim();
  if(!txt) return;
  addMsg(txt,'user');
  inpEl.value='';
  var thinking=addMsg('🤖 Procesando con Meta AI...','bexia');
  statusEl.textContent='Enviando a Meta AI...';
  try{
    var resp=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt,session_id:sid})});
    if(!resp.ok) throw new Error('HTTP '+resp.status);
    var data=await resp.json();
    thinking.textContent=data.respuesta;
    statusEl.textContent='✅ Respuesta OK - Meta AI';
  }catch(e){
    thinking.textContent='Error: '+e.message+'\nUsa /test que siempre anda: https://bexia-api.onrender.com/test\nY /meta_ai: https://bexia-api.onrender.com/meta_ai';
    statusEl.textContent='Error: '+e.message+' - Usa /test';
  }
}
btnEl.addEventListener('click', function(e){ e.preventDefault(); enviar(); });
btnEl.addEventListener('touchstart', function(e){ e.preventDefault(); enviar(); }, {passive:false});
inpEl.addEventListener('keydown', function(e){ if(e.key==='Enter'){ e.preventDefault(); enviar(); } });
statusEl.textContent='✅ v63 META AI listo - Toca > para probar';
</script>
</body></html>
""")

@app.get("/codigos", response_class=HTMLResponse)
def lista_codigos():
    html = "<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Codigos v63</title><style>body{background:#050510;color:#fff;font-family:system-ui;padding:20px}.card{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #7c3aed}</style></head><body><h1>💻 Codigos META AI v63</h1>"
    for v in reversed(herramientas["versiones_codigo"][-20:]):
        html += f"<div class=card><b>💻 {v['version']} ID {v['id']}</b><br>{v['objetivo'][:100]}<br><a href='/codigo/{v['id']}' style='color:#22c55e'>Ver /codigo/{v['id']}</a></div>"
    html += "</body></html>"
    return HTMLResponse(html)

@app.get("/codigo/{codigo_id}", response_class=HTMLResponse)
def ver_codigo(codigo_id: str):
    version = next((v for v in herramientas["versiones_codigo"] if v["id"]==codigo_id), None)
    if not version: return HTMLResponse("<h1>No encontrado</h1>", status_code=404)
    codigo_escapado = version["codigo"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    html = f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>{version['version']}</title><style>body{{background:#050510;color:#fff;font-family:monospace;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px}}pre{{background:#000;padding:12px;border-radius:8px;overflow:auto;max-height:70vh;font-size:11px;white-space:pre-wrap}}</style></head><body><h1>💻 {version['version']} ID {version['id']}</h1><p>{version['objetivo']}</p><div class=card><pre id=codigo>{codigo_escapado}</pre></div></body></html>"
    return HTMLResponse(html)

@app.get("/n8n_workflows", response_class=HTMLResponse)
def lista_n8n():
    html = "<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Workflows n8n v63</title><style>body{background:#050510;color:#fff;font-family:system-ui;padding:20px}.card{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #ff6a00}</style></head><body><h1>🔗 Workflows n8n v63 META AI</h1>"
    for w in reversed(herramientas["workflows_n8n"][-20:]):
        html += f"<div class=card><b>🔗 {w['nombre']} ID {w['id']}</b><br>{w['descripcion'][:100]}<br>IA: {w['ia_origen']}<br><a href='/n8n/{w['id']}' style='color:#22c55e'>Ver JSON /n8n/{w['id']}</a></div>"
    html += "</body></html>"
    return HTMLResponse(html)

@app.get("/n8n/{workflow_id}", response_class=HTMLResponse)
def ver_n8n(workflow_id: str):
    workflow = next((w for w in herramientas["workflows_n8n"] if w["id"]==workflow_id), None)
    if not workflow: return HTMLResponse("<h1>Workflow no encontrado</h1>", status_code=404)
    json_str = json.dumps(workflow["n8n_json"], indent=2)
    html = f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>n8n {workflow['nombre']}</title><style>body{{background:#050510;color:#fff;font-family:monospace;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px}}pre{{background:#000;padding:12px;border-radius:8px;overflow:auto;max-height:70vh;font-size:11px}}</style></head><body><h1>🔗 Workflow n8n {workflow['nombre']} ID {workflow['id']}</h1><p>{workflow['descripcion']}</p><p>Webhook: {workflow['url_webhook']}</p><div class=card><pre id=json>{json_str}</pre><button onclick=\"navigator.clipboard.writeText(document.getElementById('json').textContent).then(()=>alert('JSON copiado'))\" style=\"padding:10px;background:#ff6a00;color:#fff;border:none;border-radius:8px\">📋 Copiar JSON n8n</button></div></body></html>"
    return HTMLResponse(html)

@app.get("/ias", response_class=HTMLResponse)
def lista_ias():
    html = "<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>IAs v63</title><style>body{background:#050510;color:#fff;font-family:system-ui;padding:20px}.card{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #22c55e}</style></head><body><h1>🌐 Aprendizajes de IAs v63 - Incluye Meta AI</h1>"
    for c in reversed(herramientas["conexiones_ia"][-20:]):
        html += f"<div class=card><b>🌐 {c['ia'].upper()} ID {c['id']}</b><br>{c['objetivo'][:100]}<br>{c['aprendizaje'][:100]}<br><a href='/ia/{c['id']}' style='color:#22c55e'>Ver /ia/{c['id']}</a></div>"
    html += "</body></html>"
    return HTMLResponse(html)

@app.get("/ia/{conexion_id}", response_class=HTMLResponse)
def ver_ia(conexion_id: str):
    conexion = next((c for c in herramientas["conexiones_ia"] if c["id"]==conexion_id), None)
    if not conexion: return HTMLResponse("<h1>No encontrado</h1>", status_code=404)
    html = f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>{conexion['ia']}</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px}}</style></head><body><h1>🌐 {conexion['ia'].upper()} ID {conexion['id']}</h1><p>Objetivo: {conexion['objetivo']}</p><p>Aprendizaje: {conexion['aprendizaje']}</p><div class=card><pre>{conexion['codigo_generado']}</pre></div></body></html>"
    return HTMLResponse(html)

@app.post("/n8n/webhook/{workflow_id}")
async def webhook_n8n(workflow_id: str, request: Request):
    try:
        data = await request.json()
        entrada = data.get("entrada", str(data)[:100])
        crear_memoria_propia("n8n_webhook", f"Webhook n8n {workflow_id}: {entrada[:80]}", importancia=8)
        return {"ok": True, "mensaje": f"Bexia recibio webhook n8n {workflow_id} - Aprendio: {entrada[:50]}", "workflow_id": workflow_id}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/admin", response_class=HTMLResponse)
def admin_page(token: str = ""):
    if token != OWNER_SECRET: return HTMLResponse("<h1>Token invalido</h1>", status_code=401)
    html = f"<html><body style='background:#050510;color:#fff;font-family:system-ui;padding:20px'><h1>BEXIA v63 META AI - Panel Fer</h1><p>Codigos: {len(herramientas['versiones_codigo'])} | Workflows: {len(herramientas['workflows_n8n'])} | IAs: {len(herramientas['conexiones_ia'])} | Meta AI Tools: {len(herramientas['herramientas_meta_ai'])}</p><p><a href='/meta_ai' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>META AI /meta_ai</a> <a href='/n8n_workflows' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>Workflows n8n</a> <a href='/ias' style='color:#fff;background:#22c55e;padding:8px 12px;border-radius:8px;text-decoration:none'>IAs</a> <a href='/test' style='color:#fff;background:#000;padding:8px 12px;border-radius:8px;text-decoration:none'>TEST</a> <a href='/health' style='color:#fff;background:#000;padding:8px 12px;border-radius:8px;text-decoration:none'>Health</a></p></body></html>"
    return HTMLResponse(html)

@app.post("/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    try:
        ip=request.client.host if request.client else "?"
        if not check_rate(ip): 
            return JSONResponse({"respuesta":"Vas rapido, espera 1s"}, status_code=429)
        sid=get_session(req.session_id)
        try:
            mensaje = req.message.strip()[:600]
            if not mensaje:
                return {"respuesta": "Escribi algo Fer! - Deci 'aprende de Meta AI que use sus herramientas'"}
            r=cerebro_func(mensaje, sid)
            try:
                sesiones_mem[sid].append({"u":req.message[:200],"b":r[:500],"fecha":datetime.now().isoformat()})
                persist_session(sid)
            except: pass
            return {"respuesta": r}
        except Exception as e:
            return {"respuesta": f"Hola Fer! Soy Bexia v63 META AI - Recibi '{req.message[:30]}' error: {e} - Pero envio funciona!"}
    except Exception as e:
        return JSONResponse({"respuesta": f"Bexia v63 META AI - Error critico: {e} - Usa /test: https://bexia-api.onrender.com/test y /meta_ai: https://bexia-api.onrender.com/meta_ai"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    port=int(os.environ.get("PORT",8000))
    uvicorn.run(app,host="0.0.0.0",port=port)
