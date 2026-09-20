"""
BEXIA v67 CREA ALGO COMO META COMO CLAUDE + META AI + MULTI-IA + N8N
"""
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

print("BEXIA v67 CREA COMO META COMO CLAUDE iniciando...", flush=True)
OWNER_SECRET="BEXIA_FER_2026_INFINITA_SUPREMA"
VERSION_ACTUAL="v67"
app=FastAPI(title="BEXIA v67", docs_url=None, redoc_url=None, openapi_url=None)
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
herramientas=load_json("bexia_herramientas.json", {"sitios":[],"cache":{},"versiones_codigo":[],"workflows_n8n":[],"conexiones_ia":[],"aprendizajes_externos":[],"herramientas_meta_ai":[],"clones_creados":[]})
memoria_propia=load_json("bexia_memoria_propia.json", {"recuerdos":[],"auto_memorias":[],"commits":[],"branches":["main"]})
log_autonomo=load_json("bexia_autonomo_log.json", {"codigos_generados":[],"workflows_creados":[],"aprendizajes_multi_ia":[],"aprendizajes_meta_ai":[],"clones":[]})
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
        commit={"id": str(uuid.uuid4())[:7], "mensaje": f"{tipo}: {contenido[:50]}", "fecha": mem["fecha"], "memoria_id": mem["id"], "branch": tipo, "autor": "bexia-v67"}
        memoria_propia["commits"].append(commit)
        if len(memoria_propia["commits"])>500: memoria_propia["commits"]=memoria_propia["commits"][-300:]
        save_json("bexia_memoria_propia.json", memoria_propia)
        return mem
    except:
        return {"id":"err"}

def crear_clon_estilo_meta_ai(objetivo):
    clon_id=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    codigo_meta = "# CLON ESTILO META AI - Bexia v67\n# Objetivo: " + objetivo[:80] + "\nclass ClonMetaAI:\n    def __init__(self):\n        self.nombre='Meta AI Clone by Bexia v67'\n        self.version='v67-meta-clone-" + clon_id + "'\n        self.objetivo='" + objetivo[:100].replace("'","") + "'\n        self.herramientas=['content_search','local_search','image_gen','video_gen','python_execution']\n        self.modelo_base='Llama 4 - Meta'\n    def content_search(self, query):\n        return f'Meta AI content_search sobre {query[:30]}: posts relevantes IG, FB, Threads'\n    def local_search(self, lugar, ciudad='Chivilcoy'):\n        return f'Meta AI local_search {lugar} en {ciudad}: 5 lugares con rating'\n    def pensar_como_meta_ai(self, entrada):\n        return f'Meta AI sobre {entrada[:30]}: content_search + local_search + image_gen'\nclon_meta=ClonMetaAI()\nprint(clon_meta.pensar_como_meta_ai('" + objetivo[:20].replace("'","") + "'))\n"
    clon={
        "id": clon_id,
        "tipo": "meta_ai",
        "nombre": f"Clon Meta AI - {objetivo[:30]}",
        "objetivo": objetivo[:200],
        "codigo": codigo_meta,
        "herramientas": ["content_search","local_search","image_gen","video_gen","python_execution"],
        "estilo": "Meta AI - Social + Lugares + Visual",
        "fecha": fecha,
        "inspirado_en": "Meta AI (Llama 4)",
        "gratis": True
    }
    try:
        herramientas["clones_creados"].append(clon)
        herramientas["versiones_codigo"].append({"id": clon_id, "version": f"v67-meta-clone-{clon_id}", "objetivo": objetivo[:200], "codigo": codigo_meta, "fecha": fecha, "tipo": "clon_meta_ai", "usa_herramientas_meta_ai": True})
        save_json("bexia_herramientas.json", herramientas)
        log_autonomo["clones"].append({"id": clon_id, "tipo": "meta_ai", "fecha": fecha, "objetivo": objetivo[:40]})
        save_json("bexia_autonomo_log.json", log_autonomo)
        crear_memoria_propia("clon", f"Cree clon estilo Meta AI ID {clon_id}: {objetivo[:60]}", importancia=10)
    except: pass
    return {"ok": True, "clon": clon}

def crear_clon_estilo_claude(objetivo):
    clon_id=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    # Codigo seguro sin dynamic function names con digitos
    codigo_claude = "# CLON ESTILO CLAUDE - Bexia v67\n# Objetivo: " + objetivo[:80] + "\nclass ClonClaude:\n    def __init__(self):\n        self.nombre='Claude Clone by Bexia v67'\n        self.version='v67-claude-clone-" + clon_id + "'\n        self.objetivo='" + objetivo[:100].replace("'","") + "'\n        self.principios=['Razonamiento paso a paso','Seguro, util, honesto','Explica por que','Codigo limpio']\n    def razonar_paso_a_paso(self, problema):\n        return '1. Entender problema 2. Analizar contexto 3. Considerar opciones 4. Elegir mejor 5. Explicar por que 6. Ejemplo 7. Verificar'\n    def pensar_como_claude(self, entrada):\n        return f'Claude sobre {entrada[:30]}: razonamiento estructurado paso a paso, seguro, util'\nclon_claude=ClonClaude()\nprint(clon_claude.pensar_como_claude('" + objetivo[:20].replace("'","") + "'))\n"
    clon={
        "id": clon_id,
        "tipo": "claude",
        "nombre": f"Clon Claude - {objetivo[:30]}",
        "objetivo": objetivo[:200],
        "codigo": codigo_claude,
        "principios": ["Razonamiento estructurado", "Seguro, util, honesto", "Explica por que", "Codigo limpio"],
        "estilo": "Claude - Razonamiento paso a paso, seguro, util",
        "fecha": fecha,
        "inspirado_en": "Claude (Anthropic)",
        "gratis": True
    }
    try:
        herramientas["clones_creados"].append(clon)
        herramientas["versiones_codigo"].append({"id": clon_id, "version": f"v67-claude-clone-{clon_id}", "objetivo": objetivo[:200], "codigo": codigo_claude, "fecha": fecha, "tipo": "clon_claude"})
        save_json("bexia_herramientas.json", herramientas)
        log_autonomo["clones"].append({"id": clon_id, "tipo": "claude", "fecha": fecha, "objetivo": objetivo[:40]})
        save_json("bexia_autonomo_log.json", log_autonomo)
        crear_memoria_propia("clon", f"Cree clon estilo Claude ID {clon_id}: {objetivo[:60]}", importancia=10)
    except: pass
    return {"ok": True, "clon": clon}

def crear_clon_hibrido_meta_claude(objetivo):
    clon_id=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    codigo_hibrido = "# CLON HIBRIDO META AI + CLAUDE - Bexia v67\n# Objetivo: " + objetivo[:80] + "\nclass ClonMetaClaudeHibrido:\n    def __init__(self):\n        self.nombre='Meta+Claude Hibrido by Bexia v67'\n        self.version='v67-hibrido-" + clon_id + "'\n        self.objetivo='" + objetivo[:100].replace("'","") + "'\n        self.herramientas_meta=['content_search','local_search','image_gen']\n        self.principios_claude=['Razonamiento paso a paso','Seguro, util']\n    def pensar_hibrido(self, entrada):\n        return f'Hibrido Meta+Claude sobre {entrada[:30]}: herramientas Meta + razonamiento Claude'\nclon_hibrido=ClonMetaClaudeHibrido()\nprint(clon_hibrido.pensar_hibrido('" + objetivo[:20].replace("'","") + "'))\n"
    clon={
        "id": clon_id,
        "tipo": "hibrido_meta_claude",
        "nombre": f"Clon Hibrido Meta+Claude - {objetivo[:30]}",
        "objetivo": objetivo[:200],
        "codigo": codigo_hibrido,
        "herramientas": ["content_search","local_search","image_gen","video_gen"],
        "principios": ["Razonamiento estructurado", "Seguro, util", "Contexto social + lugares"],
        "estilo": "Hibrido Meta AI (herramientas) + Claude (razonamiento)",
        "fecha": fecha,
        "inspirado_en": "Meta AI + Claude",
        "gratis": True
    }
    try:
        herramientas["clones_creados"].append(clon)
        herramientas["versiones_codigo"].append({"id": clon_id, "version": f"v67-hibrido-{clon_id}", "objetivo": objetivo[:200], "codigo": codigo_hibrido, "fecha": fecha, "tipo": "clon_hibrido"})
        save_json("bexia_herramientas.json", herramientas)
        log_autonomo["clones"].append({"id": clon_id, "tipo": "hibrido_meta_claude", "fecha": fecha, "objetivo": objetivo[:40]})
        save_json("bexia_autonomo_log.json", log_autonomo)
        crear_memoria_propia("clon", f"Cree clon hibrido Meta+Claude ID {clon_id}: {objetivo[:60]}", importancia=10)
    except: pass
    return {"ok": True, "clon": clon}

def conectar_ia_externa(nombre_ia, objetivo_aprendizaje):
    legal, razon = es_legal(objetivo_aprendizaje)
    if not legal: return {"ok": False, "error": razon}
    conexion_id=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    aprendizajes_simulados = {
        "meta ai": f"Aprendido de Meta AI sobre {objetivo_aprendizaje[:40]}: Llama 4, content_search, local_search - Ef +15",
        "mata ai": f"Aprendido de Meta AI (typo mata) sobre {objetivo_aprendizaje[:40]}: Llama 4, herramientas Meta",
        "claude": f"Aprendido de Claude sobre {objetivo_aprendizaje[:40]}: Razonamiento estructurado paso a paso, seguro, util - Como Claude - Ef +12",
        "claude ai": f"Aprendido de Claude sobre {objetivo_aprendizaje[:40]}: Razonamiento estructurado, codigo limpio",
        "chatgpt": f"Aprendido de ChatGPT sobre {objetivo_aprendizaje[:40]}: creatividad",
        "gemini": f"Aprendido de Gemini sobre {objetivo_aprendizaje[:40]}: multimodal",
        "grok": f"Aprendido de Grok sobre {objetivo_aprendizaje[:40]}: tiempo real",
        "perplexity": f"Aprendido de Perplexity sobre {objetivo_aprendizaje[:40]}: busqueda con fuentes",
        "n8n": f"Aprendido de n8n sobre {objetivo_aprendizaje[:40]}: automatizacion"
    }
    nombre_lower = nombre_ia.lower()
    if "meta" in nombre_lower or "mata" in nombre_lower: 
        nombre_lower="meta ai"
        nombre_ia="Meta AI"
    if "claude" in nombre_lower:
        nombre_lower="claude"
        nombre_ia="Claude"
    aprendizaje = aprendizajes_simulados.get(nombre_lower, f"Aprendido de {nombre_ia} sobre {objetivo_aprendizaje[:40]}")
    herramientas_meta = []
    if "meta" in nombre_lower:
        herramientas_meta = ["content_search", "local_search", "image_gen", "video_gen"]
    conexion={
        "id": conexion_id,
        "ia": nombre_ia,
        "objetivo": objetivo_aprendizaje[:200],
        "aprendizaje": aprendizaje,
        "herramientas_meta_ai": herramientas_meta,
        "fecha": fecha,
        "estado": "aprendido",
        "gratis": True,
        "codigo_generado": f"# Aprendido de {nombre_ia}: {aprendizaje[:60]}"
    }
    try:
        herramientas["conexiones_ia"].append(conexion)
        herramientas["aprendizajes_externos"].append({"id": conexion_id, "ia": nombre_ia, "aprendizaje": aprendizaje, "fecha": fecha, "objetivo": objetivo_aprendizaje[:80]})
        if "meta" in nombre_lower:
            herramientas["herramientas_meta_ai"].append({"id": conexion_id, "herramienta": "meta_ai_tools", "aprendizaje": aprendizaje, "fecha": fecha})
        save_json("bexia_herramientas.json", herramientas)
        crear_memoria_propia("meta_ai" if "meta" in nombre_lower else "multi_ia", f"Aprendi de {nombre_ia}: {objetivo_aprendizaje[:60]}", importancia=10)
    except: pass
    return {"ok": True, "conexion": conexion}

def crear_workflow_n8n(nombre_workflow, descripcion, ia_origen="Meta AI"):
    legal, razon = es_legal(descripcion)
    if not legal: return {"ok": False, "error": razon}
    workflow_id=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    if "meta" in ia_origen.lower() or "mata" in ia_origen.lower(): ia_origen="Meta AI"
    if "claude" in ia_origen.lower(): ia_origen="Claude"
    n8n_json = {
        "name": nombre_workflow[:60],
        "nodes": [
            {"id": "1", "name": "Webhook Bexia", "type": "n8n-nodes-base.webhook", "parameters": {"path": f"bexia-{workflow_id}"}},
            {"id": "2", "name": f"{ia_origen} - Razonamiento", "type": "n8n-nodes-base.function"},
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
        crear_memoria_propia("n8n", f"Cree workflow n8n {nombre_workflow[:40]} que aprende de {ia_origen}", importancia=10)
    except: pass
    return {"ok": True, "workflow": workflow}

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
            return cache_resp + "\n\nCache v67"
        if any(p in t for p in ["crea algo como meta", "crea algo como claude", "crea como meta", "crea como claude", "algo como meta", "algo como claude", "clon como meta", "clon como claude", "haz algo como meta", "haz algo como claude"]):
            pide_meta = "meta" in t or "mata" in t
            pide_claude = "claude" in t
            objetivo = user_text
            for pref in ["crea algo como meta que", "crea algo como claude que", "crea algo como meta y claude que", "crea como meta que", "crea como claude que", "algo como meta que", "algo como claude que", "crea algo como meta", "crea algo como claude", "crea como meta", "crea como claude"]:
                if pref in t:
                    objetivo = user_text.lower().split(pref,1)[-1].strip()
                    break
            if len(objetivo)<10 or objetivo in ["crea algo como meta", "crea algo como claude"]:
                objetivo = "Asistente que ayude a Fer a organizar tareas, buscar lugares y generar contenido como Meta AI y Claude"
            if pide_meta and pide_claude:
                res = crear_clon_hibrido_meta_claude(objetivo)
                if res["ok"]:
                    c=res["clon"]
                    return f"🤖🧠 CLON HIBRIDO META AI + CLAUDE CREADO ID {c['id']}\n\nNombre: {c['nombre']}\nObjetivo: {c['objetivo']}\nEstilo: {c['estilo']}\nInspirado en: {c['inspirado_en']}\nHerramientas: {', '.join(c['herramientas'])} + Principios Claude\n\nCodigo ({len(c['codigo'].splitlines())} lineas):\n{c['codigo'][:1200]}...\n\nVer codigo completo: /codigo/{c['id']} - /clones\n\nHibrido: Herramientas Meta AI (content_search, local_search, image_gen) + Razonamiento Claude (paso a paso, seguro, util). Gratis, legal."
            elif pide_meta:
                res = crear_clon_estilo_meta_ai(objetivo)
                if res["ok"]:
                    c=res["clon"]
                    return f"🤖 CLON ESTILO META AI CREADO ID {c['id']}\n\nNombre: {c['nombre']}\nObjetivo: {c['objetivo']}\nEstilo: {c['estilo']}\nInspirado en: {c['inspirado_en']}\nHerramientas: {', '.join(c['herramientas'])}\n\nCodigo ({len(c['codigo'].splitlines())} lineas):\n{c['codigo'][:1200]}...\n\nVer codigo completo: /codigo/{c['id']} - /clones - /meta_ai\n\nClon como Meta AI: usa content_search (posts IG/FB/Threads), local_search (lugares reales), image_gen, video_gen. Gratis, legal."
            elif pide_claude:
                res = crear_clon_estilo_claude(objetivo)
                if res["ok"]:
                    c=res["clon"]
                    return f"🧠 CLON ESTILO CLAUDE CREADO ID {c['id']}\n\nNombre: {c['nombre']}\nObjetivo: {c['objetivo']}\nEstilo: {c['estilo']}\nInspirado en: {c['inspirado_en']}\nPrincipios: {', '.join(c['principios'])}\n\nCodigo ({len(c['codigo'].splitlines())} lineas):\n{c['codigo'][:1200]}...\n\nVer codigo completo: /codigo/{c['id']} - /clones - /claude_ai\n\nClon como Claude: razonamiento estructurado paso a paso, seguro, util, honesto, explica por que, codigo limpio. Gratis, legal."
            else:
                res = crear_clon_hibrido_meta_claude(objetivo)
                if res["ok"]:
                    c=res["clon"]
                    return f"🤖🧠 CLON HIBRIDO META + CLAUDE CREADO ID {c['id']} (por defecto)\nNombre: {c['nombre']}\nObjetivo: {c['objetivo']}\nCodigo: /codigo/{c['id']}"
        if any(p in t for p in ["meta ai", "mata ai", "llama"]):
            ia_detectada="Meta AI"
            objetivo = user_text
            for pref in ["aprende de meta ai que", "aprende de mata ai que"]:
                if pref in t:
                    objetivo = user_text.lower().split(pref,1)[-1].strip()
                    break
            if len(objetivo)<10: objetivo="Ser mas eficiente usa
