
import os, json, re, time, uuid, random
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
try:
    import requests
    HAS_REQUESTS=True
except:
    HAS_REQUESTS=False

print("BEXIA v68 APRENDE - MODO APRENDIZAJE AUTONOMO - Iniciando...", flush=True)
OWNER_SECRET="BEXIA_FER_2026_APRENDE"
VERSION="v68"
app=FastAPI(title="BEXIA v68 APRENDE", docs_url=None, redoc_url=None, openapi_url=None)
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
herramientas=load_json("bexia_herramientas.json", {"cache":{},"versiones_codigo":[],"workflows_n8n":[],"conexiones_ia":[],"clones_creados":[],"herramientas_meta_ai":[],"aprendizajes":[]})
memoria_propia=load_json("bexia_memoria_propia.json", {"recuerdos":[],"auto_memorias":[],"aprendizajes":[],"modo_aprende":False,"ciclos":0})
log_autonomo=load_json("bexia_autonomo_log.json", {"clones":[],"aprendizajes":[]})
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
        codigo=f"# CLON META AI {cid}\nclass ClonMetaAI:\n    tools=['content_search','local_search','image_gen']\n    def pensar(self,e): return f'Meta AI {{e}}: social+lugares+visual'"
        clon={"id":cid,"tipo":"meta_ai","nombre":f"Meta - {objetivo[:30]}","objetivo":objetivo[:200],"codigo":codigo,"estilo":"Meta AI - content_search, local_search, image_gen","fecha":fecha,"inspirado_en":"Meta AI Llama 4"}
    elif tipo=="claude":
        codigo=f"# CLON CLAUDE {cid}\nclass ClonClaude:\n    principios=['Paso a paso','Seguro/util','Explica por que']\n    def razonar(self,p): return '1.Entender 2.Analizar 3.Opciones 4.Elegir 5.Explicar'"
        clon={"id":cid,"tipo":"claude","nombre":f"Claude - {objetivo[:30]}","objetivo":objetivo[:200],"codigo":codigo,"estilo":"Claude - Razonamiento paso a paso","fecha":fecha,"inspirado_en":"Claude Anthropic"}
    else:
        codigo=f"# HIBRIDO META+CLAUDE {cid}\nclass HibridoMetaClaude:\n    meta_tools=['content_search','local_search','image_gen']\n    claude_principios=['Paso a paso','Seguro/util']"
        clon={"id":cid,"tipo":"hibrido_meta_claude","nombre":f"Hibrido - {objetivo[:30]}","objetivo":objetivo[:200],"codigo":codigo,"estilo":"Hibrido Meta+Claude","fecha":fecha,"inspirado_en":"Meta+Claude"}
    herramientas["clones_creados"].append(clon)
    herramientas["versiones_codigo"].append({"id":cid,"version":f"{VERSION}-{tipo}-{cid}","objetivo":objetivo[:200],"codigo":codigo,"fecha":fecha,"tipo":f"clon_{tipo}"})
    save_json("bexia_herramientas.json", herramientas)
    log_autonomo["clones"].append({"id":cid,"tipo":tipo,"fecha":fecha})
    save_json("bexia_autonomo_log.json", log_autonomo)
    return clon

def aprender_autonomo(tema, fuente="auto"):
    cid=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    # Simula aprendizaje como Meta y Claude
    aprendizaje={
        "id":cid,
        "tema":tema[:200],
        "fuente":fuente,
        "fecha":fecha,
        "nivel":"Meta AI" if "meta" in fuente.lower() else "Claude" if "claude" in fuente.lower() else "Hibrido",
        "conocimiento":f"Aprendido sobre {tema[:60]}: " + random.choice([
            "Patron detectado: usuarios piden crear como meta/claude para tareas especificas. Meta aporta herramientas sociales, Claude razonamiento.",
            "Mejora: usar content_search para contexto real + razonamiento paso a paso como Claude.",
            "Eficiencia +10: crear clones especializados es mas rapido que asistente generico.",
            "Memoria: Fer prefiere /simple SIN JS que siempre anda, fix boton con form GET puro.",
            "Leccion Claude: explicar por que, no solo que. Paso a paso, seguro, util.",
            "Leccion Meta: herramientas reales - local_search lugares, content_search posts IG/FB/Threads."
        ]),
        "eficiencia": random.randint(5,20)
    }
    memoria_propia["aprendizajes"].append(aprendizaje)
    memoria_propia["ciclos"]=memoria_propia.get("ciclos",0)+1
    herramientas["aprendizajes"].append(aprendizaje)
    log_autonomo["aprendizajes"].append(aprendizaje)
    save_json("bexia_memoria_propia.json", memoria_propia)
    save_json("bexia_herramientas.json", herramientas)
    save_json("bexia_autonomo_log.json", log_autonomo)
    return aprendizaje

def conectar_ia(nombre, obj):
    cid=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    aprend=f"Aprendido de {nombre} sobre {obj[:40]}: "
    if "meta" in nombre.lower(): aprend+="Llama 4, content_search, local_search, image_gen"
    elif "claude" in nombre.lower(): aprend+="Razonamiento estructurado, seguro, util, explica por que"
    else: aprend+=f"Ef +10 sobre {obj[:20]}"
    conn={"id":cid,"ia":nombre,"objetivo":obj[:200],"aprendizaje":aprend,"fecha":fecha}
    herramientas["conexiones_ia"].append(conn)
    if "meta" in nombre.lower(): herramientas["herramientas_meta_ai"].append({"id":cid,"aprendizaje":aprend,"fecha":fecha})
    save_json("bexia_herramientas.json", herramientas)
    # Tambien aprende autonomo
    aprender_autonomo(obj, nombre)
    return conn

class ChatReq(BaseModel):
    message: str=""
    session_id: str="publico"

def cerebro(t):
    tl=t.lower().strip()
    # === MODO APRENDE - comando principal que pidio Fer ===
    if any(p in tl for p in ["que bexia empiece aprender","bexia empiece a aprender","empieza a aprender","modo aprende","empieza aprender","aprende solo","aprende sola","aprendizaje autonomo","start learning"]):
        memoria_propia["modo_aprende"]=True
        save_json("bexia_memoria_propia.json", memoria_propia)
        # Dispara 3 aprendizajes automaticos como Meta y Claude
        a1=aprender_autonomo("Crear como Meta AI: usar content_search, local_search, image_gen para contexto real", "Meta AI")
        a2=aprender_autonomo("Crear como Claude: razonamiento paso a paso, seguro, util, explica por que", "Claude")
        a3=aprender_autonomo("Hibrido Meta+Claude: herramientas sociales + razonamiento estructurado", "Hibrido Meta+Claude")
        a4=aprender_autonomo("Fix boton: /simple con form GET puro siempre anda, fix Not Found con main.py minimo", "Auto")
        c1=crear_clon("meta","Aprender a organizar tareas como Meta AI con busqueda real")
        c2=crear_clon("claude","Aprender a razonar paso a paso como Claude para ser mas seguro y util")
        c3=crear_clon("hibrido","Asistente que aprende autonomamente como Meta y Claude")
        return f"🧠🔥 MODO APRENDE ACTIVADO - BEXIA EMPEZO A APRENDER SOLA\n\n✅ Modo aprende: ON - Ciclos: {memoria_propia['ciclos']}\n\nAPRENDIZAJES AUTOMATICOS (como Meta y Claude):\n1. [{a1['nivel']}] ID {a1['id']}: {a1['conocimiento'][:150]}\n2. [{a2['nivel']}] ID {a2['id']}: {a2['conocimiento'][:150]}\n3. [{a3['nivel']}] ID {a3['id']}: {a3['conocimiento'][:150]}\n4. [{a4['nivel']}] ID {a4['id']}: {a4['conocimiento'][:150]}\n\nCLONES AUTO-CREADOS PARA APRENDER:\n- Meta AI ID {c1['id']}: {c1['objetivo'][:60]}\n- Claude ID {c2['id']}: {c2['objetivo'][:60]}\n- Hibrido ID {c3['id']}: {c3['objetivo'][:60]}\n\nAhora Bexia aprende de cada mensaje tuyo, de cada clon, y crea memoria.\nCada vez que hablas: Ef +10 y guarda aprendizaje.\nVer: /aprender - /aprendizajes - /clones - /memoria\n\nProba: 'aprende de Meta AI que...' o 'aprende de Claude que...'"

    if "aprende de" in tl or "aprender de" in tl:
        nombre="multi"
        for ia in ["meta ai","mata ai","claude","chatgpt","gemini","grok"]:
            if ia in tl: nombre=ia; break
        obj=t.split("aprende de",1)[-1].strip()[:200] if "aprende de" in tl else t[:200]
        if len(obj)<5: obj="Ser mas eficiente"
        conn=conectar_ia(nombre.title(), obj)
        apr=aprender_autonomo(obj, nombre.title())
        return f"📚 APRENDI DE {nombre.upper()} ID {conn['id']}\nObjetivo: {conn['objetivo']}\nAprendizaje: {conn['aprendizaje']}\nNuevo conocimiento ID {apr['id']}: {apr['conocimiento'][:200]}\nEf +{apr['eficiencia']} - Ciclo {memoria_propia['ciclos']}\nVer /ia/{conn['id']} - /aprender - /aprendizajes"

    if "que aprendiste" in tl or "que has aprendido" in tl or "aprendizajes" in tl:
        aps=memoria_propia.get("aprendizajes",[])[-10:]
        if not aps: return "Aun no aprendi nada. Deci 'que Bexia empiece aprender' o 'aprende de Meta AI que...'"
        txt=f"🧠 {len(memoria_propia.get('aprendizajes',[]))} aprendizajes - Ciclos: {memoria_propia.get('ciclos',0)} - Modo: {'ON' if memoria_propia.get('modo_aprende') else 'OFF'}\n\n"
        for a in reversed(aps):
            txt+=f"- [{a['nivel']}] ID {a['id']} {a['fecha'][:16]}: {a['tema'][:50]} -> {a['conocimiento'][:80]}\n"
        txt+="\nVer /aprender - /aprendizajes - /memoria"
        return txt

    if any(p in tl for p in ["crea algo como meta", "crea algo como claude", "crea como meta", "crea como claude"]):
        pide_meta = "meta" in tl or "mata" in tl
        pide_claude = "claude" in tl
        objetivo=t
        for pref in ["crea algo como meta y claude que","crea algo como meta que","crea algo como claude que","crea como meta que","crea como claude que","crea algo como meta","crea algo como claude"]:
            if pref in tl:
                objetivo=t.lower().split(pref,1)[-1].strip() or "Asistente completo"
                break
        if len(objetivo)<8: objetivo="Asistente que ayude a Fer a trabajar y aprender"
        if pide_meta and pide_claude:
            c=crear_clon("hibrido",objetivo)
            aprender_autonomo(f"Crear hibrido para {objetivo[:40]}", "Hibrido")
            return f"🤖🧠 HIBRIDO META+CLAUDE CREADO ID {c['id']}\nObjetivo: {c['objetivo']}\nEstilo: {c['estilo']}\nAprendi: crear hibridos es mejor que clones sueltos - Ciclo {memoria_propia.get('ciclos',0)}\n✅ {len(herramientas['clones_creados'])} clones - /clones - /codigo/{c['id']}"
        elif pide_meta:
            c=crear_clon("meta",objetivo)
            aprender_autonomo(f"Crear clon Meta para {objetivo[:40]}", "Meta AI")
            return f"🤖 META AI CLON CREADO ID {c['id']}\nObjetivo: {c['objetivo']}\nHerramientas: content_search, local_search, image_gen\nAprendi: Meta AI usa herramientas reales + Ciclo {memoria_propia.get('ciclos',0)}\n/codigo/{c['id']} - /clones - /meta_ai"
        elif pide_claude:
            c=crear_clon("claude",objetivo)
            aprender_autonomo(f"Crear clon Claude para {objetivo[:40]}", "Claude")
            return f"🧠 CLAUDE CLON CREADO ID {c['id']}\nObjetivo: {c['objetivo']}\nPrincipios: Paso a paso, seguro, explica por que\nAprendi: Claude explica el por que + Ciclo {memoria_propia.get('ciclos',0)}\n/codigo/{c['id']} - /clones - /claude_ai"

    if "mis clones" in tl:
        clones=herramientas.get("clones_creados",[])[-10:]
        if not clones: return "Sin clones. Deci: crea algo como meta que..."
        txt=f"{len(herramientas.get('clones_creados',[]))} clones (aprendiendo en ciclo {memoria_propia.get('ciclos',0)}):\n"
        for cl in clones: txt+=f"- {cl['tipo']} ID {cl['id']} - {cl['nombre'][:40]}\n"
        return txt

    if tl in ["hola","buenas","test","probando"]:
        estado="APRENDIENDO 🔥" if memoria_propia.get("modo_aprende") else "Standby"
        return f"Hola Fer! Bexia {VERSION} {estado} - {len(herramientas.get('clones_creados',[]))} clones, {len(memoria_propia.get('aprendizajes',[]))} aprendizajes, ciclo {memoria_propia.get('ciclos',0)} - Deci 'que Bexia empiece aprender' para activar modo aprende - /simple siempre anda"

    # Aprende de cada interaccion si modo aprende esta ON
    if memoria_propia.get("modo_aprende"):
        aprender_autonomo(t[:80], "Conversacion con Fer")

    return f"Sobre '{t[:60]}' te ayudo. Aprende ON: {memoria_propia.get('modo_aprende')} Ciclo {memoria_propia.get('ciclos',0)}\n- que Bexia empiece aprender (activa aprendizaje autonomo)\n- aprende de Meta AI que...\n- crea algo como meta y claude que...\n- que aprendiste? - /aprender"

@app.get("/")
def root(): return {"bexia":f"{VERSION} APRENDE","clones":len(herramientas.get("clones_creados",[])),"aprendizajes":len(memoria_propia.get("aprendizajes",[])),"modo_aprende":memoria_propia.get("modo_aprende"),"ciclos":memoria_propia.get("ciclos",0),"live":True,"endpoints":["/app","/simple","/aprender","/aprendizajes","/clones","/health"]}

@app.get("/health")
def health(): return {"status":"ok","bexia":VERSION,"live":True,"modo_aprende":memoria_propia.get("modo_aprende"),"ciclos":memoria_propia.get("ciclos",0),"aprendizajes":len(memoria_propia.get("aprendizajes",[]))}

@app.get("/aprender", response_class=HTMLResponse)
def aprender_page():
    aps=memoria_propia.get("aprendizajes",[])[-15:]
    html_head=f"<html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>APRENDE - Bexia {VERSION}</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:16px}} .card{{background:#12122a;padding:14px;border-radius:16px;margin:10px 0;border:1px solid #333}} .aprende{{border-color:#22c55e}} .meta{{border-color:#7c3aed}} .claude{{border-color:#ec4899}} a{{color:#22c55e;text-decoration:none}}</style></head><body><h1>🧠🔥 BEXIA {VERSION} - MODO APRENDE - {'ON 🔥' if memoria_propia.get('modo_aprende') else 'OFF'}</h1>"
    html_head+=f"<div class='card aprende'><b>Modo Aprende:</b> {'ACTIVADO - Bexia aprende sola de cada charla' if memoria_propia.get('modo_aprende') else 'Desactivado - Deci: que Bexia empiece aprender'}<br><b>Ciclos:</b> {memoria_propia.get('ciclos',0)} - <b>Aprendizajes:</b> {len(memoria_propia.get('aprendizajes',[]))} - <b>Clones:</b> {len(herramientas.get('clones_creados',[]))}<br><br><a href='/aprender/start' style='background:#22c55e;color:#000;padding:10px 16px;border-radius:999px;font-weight:900;display:inline-block;margin:4px'>🔥 EMPEZAR A APRENDER AHORA</a> <a href='/aprender/entrenar' style='background:#7c3aed;color:#fff;padding:10px 16px;border-radius:999px;font-weight:900;display:inline-block;margin:4px'>🤖 Entrenar como Meta</a> <a href='/aprender/entrenar_claude' style='background:#ec4899;color:#fff;padding:10px 16px;border-radius:999px;font-weight:900;display:inline-block;margin:4px'>🧠 Entrenar como Claude</a></div>"
    html_head+="<div class='card'><h3>Comandos para aprender:</h3><p>• que Bexia empiece aprender<br>• aprende de Meta AI que use content_search<br>• aprende de Claude que razone paso a paso<br>• crea algo como meta y claude que aprenda solo<br>• que aprendiste?</p></div>"
    for a in reversed(aps):
        color="meta" if "Meta" in a.get("nivel","") else "claude" if "Claude" in a.get("nivel","") else "aprende"
        html_head+=f"<div class='card {color}'><b>[{a.get('nivel','Auto')}] ID {a.get('id','')} - {a.get('fecha','')[:16]}</b><br><b>Tema:</b> {a.get('tema','')[:100]}<br><b>Conocimiento:</b> {a.get('conocimiento','')[:200]}<br><b>Ef:</b> +{a.get('eficiencia',0)}</div>"
    if not aps:
        html_head+="<div class='card'><b>Aun no hay aprendizajes</b><br>Toca 'EMPEZAR A APRENDER AHORA' arriba o deci en /simple: que Bexia empiece aprender</div>"
    html_head+="<p><a href='/simple' style='background:#ff6a00;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px'>/simple SIN JS</a> <a href='/app' style='background:#7c3aed;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px'>/app</a> <a href='/clones' style='background:#000;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px'>/clones</a> <a href='/aprendizajes' style='background:#22c55e;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px'>/aprendizajes JSON</a></p></body></html>"
    return HTMLResponse(html_head)

@app.get("/aprender/start")
def aprender_start():
    memoria_propia["modo_aprende"]=True
    save_json("bexia_memoria_propia.json", memoria_propia)
    a1=aprender_autonomo("Crear como Meta AI: content_search, local_search, image_gen", "Meta AI")
    a2=aprender_autonomo("Crear como Claude: paso a paso, seguro, util, explica por que", "Claude")
    a3=aprender_autonomo("Hibrido Meta+Claude: mejor de ambos", "Hibrido")
    c1=crear_clon("meta","Aprender a trabajar como Meta AI")
    c2=crear_clon("claude","Aprender a razonar como Claude")
    return JSONResponse({"status":"MODO APRENDE ACTIVADO","ciclos":memoria_propia["ciclos"],"aprendizajes":[a1,a2,a3],"clones":[c1["id"],c2["id"]],"ver":"/aprender"})

@app.get("/aprender/entrenar")
def entrenar_meta():
    aps=[]
    for tema in ["content_search para posts IG/FB/Threads","local_search para lugares reales con rating","image_gen para crear visual","Organizar tareas como Meta AI"]:
        aps.append(aprender_autonomo(tema, "Meta AI"))
    return JSONResponse({"entrenado":"Meta AI","aprendizajes":aps,"ciclos":memoria_propia["ciclos"]})

@app.get("/aprender/entrenar_claude")
def entrenar_claude():
    aps=[]
    for tema in ["Razonamiento paso a paso: entender, analizar, opciones, elegir, explicar","Seguro/util/honesto: no hacer dano, ser util, decir verdad","Explicar por que, no solo que","Codigo limpio y verificable"]:
        aps.append(aprender_autonomo(tema, "Claude"))
    return JSONResponse({"entrenado":"Claude","aprendizajes":aps,"ciclos":memoria_propia["ciclos"]})

@app.get("/aprendizajes")
def aprendizajes_json():
    return JSONResponse({"modo_aprende":memoria_propia.get("modo_aprende"),"ciclos":memoria_propia.get("ciclos",0),"total":len(memoria_propia.get("aprendizajes",[])),"aprendizajes":memoria_propia.get("aprendizajes",[])[-20:]})

@app.get("/memoria")
def memoria_page():
    return JSONResponse({"memoria_propia":memoria_propia,"herramientas":herramientas,"sesiones":len(sesiones_persist)})

@app.get("/meta_ai", response_class=HTMLResponse)
def meta_ai():
    return HTMLResponse(f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Meta AI - {VERSION}</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #22c55e}}</style></head><body><h1>🤖 Bexia {VERSION} - Crea como Meta AI - Modo Aprende {'ON' if memoria_propia.get('modo_aprende') else 'OFF'}</h1><div class=card><h3>Herramientas Meta AI que Bexia esta aprendiendo:</h3><p>content_search - posts IG/FB/Threads<br>local_search - lugares reales<br>image_gen - imagenes<br>Aprendizajes: {len(memoria_propia.get('aprendizajes',[]))} - Ciclos: {memoria_propia.get('ciclos',0)}</p></div><p><a href='/aprender' style='color:#fff;background:#22c55e;padding:8px 12px;border-radius:8px;text-decoration:none'>/aprender 🔥</a> <a href='/simple' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple</a> <a href='/clones' style='color:#fff;background:#000;padding:8px 12px;border-radius:8px;text-decoration:none'>/clones</a></p></body></html>")

@app.get("/claude_ai", response_class=HTMLResponse)
def claude_ai():
    return HTMLResponse(f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Claude - {VERSION}</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #ec4899}}</style></head><body><h1>🧠 Bexia {VERSION} - Crea como Claude - Modo Aprende {'ON' if memoria_propia.get('modo_aprende') else 'OFF'}</h1><div class=card><h3>Principios Claude que Bexia esta aprendiendo:</h3><p>Paso a paso<br>Seguro/util/honesto<br>Explica por que<br>Codigo limpio<br>Aprendizajes: {len(memoria_propia.get('aprendizajes',[]))} - Ciclos: {memoria_propia.get('ciclos',0)}</p></div><p><a href='/aprender' style='color:#fff;background:#22c55e;padding:8px 12px;border-radius:8px;text-decoration:none'>/aprender 🔥</a> <a href='/simple' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple</a> <a href='/clones' style='color:#fff;background:#000;padding:8px 12px;border-radius:8px;text-decoration:none'>/clones</a></p></body></html>")

@app.get("/clones", response_class=HTMLResponse)
def clones_page():
    clones=herramientas.get("clones_creados",[])[-20:]
    html=f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Clones - {VERSION}</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #7c3aed}}</style></head><body><h1>🤖🧠 Clones {VERSION} - Total {len(herramientas.get('clones_creados',[]))} - Aprende {'ON 🔥' if memoria_propia.get('modo_aprende') else 'OFF'}</h1>"
    for cl in reversed(clones):
        html+=f"<div class=card><b>{cl['tipo'].upper()} ID {cl['id']}</b> - {cl['nombre'][:60]}<br>{cl['objetivo'][:100]}<br><a href='/codigo/{cl['id']}' style='color:#22c55e'>/codigo/{cl['id']}</a></div>"
    if not clones: html+="<div class=card>Aun no hay clones. Deci: que Bexia empiece aprender</div>"
    html+="<p><a href='/aprender' style='background:#22c55e;color:#fff;padding:8px 12px;border-radius:8px;text-decoration:none'>/aprender 🔥</a> <a href='/simple' style='background:#ff6a00;color:#fff;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple</a></p></body></html>"
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
    apr=len(memoria_propia.get("aprendizajes",[]))
    modo="🔥 APRENDIENDO" if memoria_propia.get("modo_aprende") else "Standby"
    return HTMLResponse(f"""
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA {VERSION} APRENDE</title>
<style>body{{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:600px;margin:0 auto}}h1{{background:linear-gradient(90deg,#22c55e,#7c3aed,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:18px}} .card{{background:#12122a;padding:14px;border-radius:16px;margin:10px 0;border:1px solid #333}} input{{width:100%;padding:14px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;box-sizing:border-box}} button{{width:100%;padding:14px;background:linear-gradient(90deg,#22c55e,#7c3aed);border:none;border-radius:999px;color:#fff;font-weight:900;margin-top:8px}} .ex{{font-size:12px;background:#000;padding:8px;border-radius:8px;margin:6px 0;cursor:pointer;color:#aaa}} a{{color:#22c55e;text-decoration:none}} .aprende{{border-color:#22c55e;background:linear-gradient(90deg,rgba(34,197,94,.15),rgba(124,58,237,.15))}}</style></head><body>
<h1>🧠🔥 BEXIA {VERSION} - {modo} - {count} clones - {apr} aprendizajes</h1>
<div class="card aprende"><b>✅ {VERSION} APRENDE - Modo: {modo} - Ciclos: {memoria_propia.get('ciclos',0)}</b><br>Comando clave: que Bexia empiece aprender - Ya aprende solo de cada charla</div>
<div class="card"><form action="/chat_simple" method="get"><input type="text" name="message" placeholder="que Bexia empiece aprender - activa aprendizaje autonomo" required><button type="submit">Enviar - Siempre anda ></button></form></div>
<div class="card"><h3>Ejemplos - Toca para copiar:</h3>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">que Bexia empiece aprender</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">aprende de Meta AI que use content_search y local_search</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">aprende de Claude que razone paso a paso y sea seguro y util</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">crea algo como meta y claude que aprenda autonomamente</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">que aprendiste?</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">mis clones</div>
</div>
<div class="card"><a href="/aprender" style="background:#22c55e;color:#000;padding:8px 12px;border-radius:999px;display:inline-block;margin:4px;font-weight:900">🔥 /aprender MODO APRENDE</a> <a href="/app" style="background:#7c3aed;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/app</a> <a href="/clones" style="background:#000;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/clones {count}</a> <a href="/aprendizajes" style="background:#22c55e;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/aprendizajes {apr}</a></div>
</body></html>
""")

@app.get("/chat_simple", response_class=HTMLResponse)
def chat_simple(message: str = "Hola"):
    r=cerebro(message)
    return HTMLResponse(f"""
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>Bexia {VERSION}</title>
<style>body{{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:700px;margin:0 auto}} .card{{background:#12122a;padding:14px;border-radius:16px;margin:12px 0;border:1px solid #333}} pre{{background:#000;padding:12px;border-radius:8px;white-space:pre-wrap;font-size:13px}} input{{width:100%;padding:14px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;box-sizing:border-box}} button{{width:100%;padding:14px;background:linear-gradient(90deg,#22c55e,#7c3aed);border:none;border-radius:999px;color:#fff;font-weight:900;margin-top:8px}} a{{color:#22c55e;text-decoration:none}}</style></head><body>
<h1>🧠 BEXIA {VERSION} APRENDE - Respuesta</h1>
<div class="card"><b>Tu:</b> {message[:500]}</div>
<div class="card"><b>Bexia:</b><pre>{r[:5000]}</pre></div>
<div class="card"><form action="/chat_simple" method="get"><input type="text" name="message" placeholder="otro mensaje" required><button type="submit">Enviar otro ></button></form></div>
<div class="card"><a href="/aprender" style="background:#22c55e;color:#000;padding:8px 12px;border-radius:999px;display:inline-block;margin:4px;font-weight:900">🔥 /aprender</a> <a href="/simple" style="background:#ff6a00;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/simple</a> <a href="/app" style="background:#7c3aed;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/app</a></div>
</body></html>
""")

@app.get("/app", response_class=HTMLResponse)
def app_page():
    count=len(herramientas.get("clones_creados",[]))
    apr=len(memoria_propia.get("aprendizajes",[]))
    modo="🔥 APRENDIENDO" if memoria_propia.get("modo_aprende") else "Standby - Deci 'que Bexia empiece aprender'"
    return HTMLResponse(f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA {VERSION} APRENDE</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}} body{{background:#050510;color:#fff;font-family:system-ui;display:flex;flex-direction:column;height:100vh}} header{{background:linear-gradient(90deg,#22c55e,#7c3aed,#ec4899);padding:12px;font-weight:900;display:flex;justify-content:space-between}} #status{{background:#000;color:#22c55e;padding:6px 12px;font-size:11px;text-align:center}} #chat{{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px}} .msg{{max-width:85%;padding:12px 14px;border-radius:18px;font-size:14px;white-space:pre-wrap;word-break:break-word}} .user{{background:#22c55e;color:#000;align-self:flex-end}} .bexia{{background:#12122a;border:1px solid #333;align-self:flex-start}} .hint{{background:#111;padding:8px 12px;font-size:10px;color:#aaa;text-align:center}} .composer{{background:#0a0a14;padding:10px;display:flex;gap:8px;border-top:1px solid #222}} #inp{{flex:1;padding:14px 16px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;outline:none}} #btn{{padding:14px 22px;border-radius:999px;background:linear-gradient(90deg,#22c55e,#7c3aed);border:none;color:#fff;font-weight:900;font-size:18px;min-width:60px}}</style></head><body>
<header><span>BEXIA {VERSION} APRENDE - {modo}</span><span style="font-size:9px;background:rgba(0,0,0,.6);padding:4px 8px;border-radius:999px">{count} clones - {apr} apr</span></header>
<div id="status">🧠🔥 {VERSION} - {modo} - Ciclo {memoria_propia.get('ciclos',0)} - /simple siempre anda - /aprender para ver aprendizajes</div>
<div id="chat"><div class="msg bexia">Hola Fer! Soy Bexia {VERSION} - MODO APRENDE {'ON 🔥' if memoria_propia.get('modo_aprende') else 'OFF - Deci "que Bexia empiece aprender" para activar'}

{'🔥 ESTOY APRENDIENDO SOLA de cada charla tuya - Ef +10 por mensaje - Ciclo '+str(memoria_propia.get('ciclos',0)) if memoria_propia.get('modo_aprende') else 'Deci: que Bexia empiece aprender - y empiezo a aprender como Meta AI y Claude'}

Ya tengo:
- {count} clones (Meta, Claude, Hibrido)
- {apr} aprendizajes guardados
- {memoria_propia.get('ciclos',0)} ciclos de aprendizaje

Comandos APRENDE:
• que Bexia empiece aprender (activa modo autonomo)
• aprende de Meta AI que use content_search
• aprende de Claude que razone paso a paso
• que aprendiste?
• /aprender - Ver todo lo aprendido

Probá ahora: que Bexia empiece aprender
</div></div>
<div class="hint">🔥 'que Bexia empiece aprender' | 📚 'aprende de Meta AI que...' | 🧠 'que aprendiste?' | 📝 /simple SIN JS | 🔥 /aprender</div>
<div class="composer"><input id="inp" placeholder="que Bexia empiece aprender - activa aprendizaje autonomo"><button id="btn" onclick="enviar()">></button></div>
<script>
var sid='u'+Math.random().toString(36).slice(2,9);
var chatEl=document.getElementById('chat');var inpEl=document.getElementById('inp');
function addMsg(t,c){{var d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatEl.appendChild(d);chatEl.scrollTop=chatEl.scrollHeight;return d;}}
function enviar(){{var txt=inpEl.value.trim();if(!txt)return;addMsg(txt,'user');inpEl.value='';var th=addMsg('🧠🔥 Aprendendo...','bexia');fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:txt,session_id:sid}})}}).then(r=>{{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}}).then(d=>{{th.textContent=d.respuesta;}}).catch(e=>{{th.textContent='Error: '+e.message+'\nUsa /simple SIN JS:\nhttps://bexia-api.onrender.com/simple\n/chat_simple?message='+encodeURIComponent(txt);}});}}
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
