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
    codigo_claude = "# CLON ESTILO CLAUDE - Bexia v67\n# Objetivo: " + objetivo[:80] + "\nclass ClonClaude:\n    def __init__(self):\n        self.nombre='Claude Clone by Bexia v67'\n        self.version='v67-claude-clone-" + clon_id + "'\n        self.objetivo='" + objetivo[:100].replace("'","") + "'\n        self.principios=['Razonamiento paso a paso','Seguro, util, honesto','Explica por que','Codigo limpio']\n    def razonar_paso_a_paso(self, problema):\n        return '1. Entender problema 2. Analizar contexto 3. Considerar opciones 4. Elegir mejor 5. Explicar por que 6. Ejemplo 7. Verificar'\n    def pensar_como_claude(self, entrada):\n        return f'Claude
...
... 759 lineas total - toca COPIAR TODO para copiar completo ...
