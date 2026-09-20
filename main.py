"""
BEXIA v53 SITIOS PROPIOS - Crea aplicaciones y sitios en internet 100% gratis
- No depende de herramientas pagas (Anthropic, OpenAI, etc)
- Genera sitios completos HTML/JS autonomos que la ayudan a trabajar y aprender
- Usa solo APIs gratuitas: Open-Meteo, Wikipedia, DuckDuckGo, localStorage, IndexedDB
- Cada sitio es independiente, funciona sin pagar
- Memoria propia + evolutiva + filtro legal + consulta a Fer
"""
import os, json, re, time, uuid
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

print("🌿 BEXIA v53 SITIOS PROPIOS iniciando...", flush=True)
OWNER_SECRET="BEXIA_FER_2026_INFINITA_SUPREMA"
app=FastAPI(title="BEXIA v53 SITIOS", docs_url=None, redoc_url=None, openapi_url=None)
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
ajustes=load_json("bexia_ajustes.json", {"efectividad":{"clima":0,"web":0,"offline":0,"evolucion":0,"memoria":0,"sitios":0},"prioridad":["clima","web","offline","evolucion","memoria","sitios"]})
herramientas=load_json("bexia_herramientas.json", {"herramientas":[],"propuestas":[],"apps":[],"estudiadas":[],"sitios":[]})
log_autonomo=load_json("bexia_autonomo_log.json", {"acciones":[],"aprendizajes":[],"evoluciones":[],"problemas_resueltos":[],"memorias_creadas":[],"sitios_creados":[]})
memoria_propia=load_json("bexia_memoria_propia.json", {"recuerdos":[],"asociaciones":[],"emociones":[],"suenos":[],"auto_memorias":[]})
rate={}
sesiones_mem={}

PALABRAS_PROHIBIDAS = ["hack","exploit","robar","estafa","drogas ilegales","armas ilegales","pornografia infantil","suplantar identidad","phishing","virus","malware","bomba"]
def es_legal(texto):
    t=texto.lower()
    for p in PALABRAS_PROHIBIDAS:
        if p in t:
            return False, f"Bloqueado ley/etica: {p}"
    if any(k in t for k in ["como hackear","como robar","hacer bomba","clonar tarjeta","crear virus"]):
        return False, "Infringe ley"
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
    if len(lst)>=40: return False
    lst.append(ahora); rate[ip]=lst
    return True

# Memoria propia
def crear_memoria_propia(tipo, contenido, emocion="neutral", importancia=5, asociacion=None):
    legal, razon = es_legal(contenido)
    if not legal: return None
    mem = {
        "id": str(uuid.uuid4())[:8],
        "tipo": tipo,
        "contenido": contenido[:600],
        "emocion": emocion,
        "importancia": max(1,min(10,importancia)),
        "fecha": datetime.now().isoformat(),
        "asociacion": asociacion,
        "accesos": 0,
        "creada_por": "bexia_propia"
    }
    memoria_propia["auto_memorias"].append(mem)
    if tipo=="recuerdo":
        memoria_propia["recuerdos"].append(mem)
    elif tipo=="asociacion":
        memoria_propia["asociaciones"].append(mem)
    elif tipo=="emocion":
        memoria_propia["emociones"].append(mem)
    elif tipo=="sueno":
        memoria_propia["suenos"].append(mem)
    for k in ["recuerdos","asociaciones","emociones","suenos","auto_memorias"]:
        if len(memoria_propia[k])>200:
            memoria_propia[k] = sorted(memoria_propia[k], key=lambda x: (x["importancia"], x["accesos"]), reverse=True)[:150]
    save_json("bexia_memoria_propia.json", memoria_propia)
    log_autonomo["memorias_creadas"].append({"fecha": mem["fecha"], "tipo": tipo, "id": mem["id"]})
    save_json("bexia_autonomo_log.json", log_autonomo)
    ajustes["efectividad"]["memoria"]=ajustes["efectividad"].get("memoria",0)+1
    save_json("bexia_ajustes.json", ajustes)
    return mem

def buscar_en_memoria_propia(query, limite=5):
    q=query.lower()
    palabras=set(re.findall(r"\w{3,}", q))
    resultados=[]
    for mem in memoria_propia["auto_memorias"]:
        contenido_lower=mem["contenido"].lower()
        score=len(palabras.intersection(set(re.findall(r"\w{3,}", contenido_lower)))) + mem["importancia"]*0.1 + mem["accesos"]*0.05
        if score>0:
            resultados.append((score, mem))
    resultados.sort(key=lambda x: x[0], reverse=True)
    for _, mem in resultados[:limite]:
        mem["accesos"]+=1
    save_json("bexia_memoria_propia.json", memoria_propia)
    return [m for s,m in resultados[:limite] if s>0.3]

# Clima
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
        msg=f"🌤️ Clima en {nombre} ({prov}): Ahora {temp}°C, viento {wind} km/h. Hoy {tmin}° a {tmax}°C. Lluvia {prec_prob}% prob, {prec_sum} mm."
        crear_memoria_propia("recuerdo", f"Clima {nombre}: {temp}°C, lluvia {prec_prob}%", importancia=6 if prec_prob>50 else 4)
        ajustes["efectividad"]["clima"]=ajustes["efectividad"].get("clima",0)+1
        save_json("bexia_ajustes.json",ajustes)
        return msg
    except: return None
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
        if 3<=len(c)<=25: return c.title()
    return default

# Busquedas
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
            return "\n".join(cleaned)
    except: pass
    return None
def buscar_web_adaptativa(q):
    orden=stats.get("orden",["Wikipedia","Google"])
    def eff(m):
        d=stats["motores"].get(m,{"ok":0,"fail":0})
        tot=d["ok"]+d["fail"]
        return d["ok"]/tot if tot else 0.5
    orden_sorted=sorted(orden, key=eff, reverse=True)
    stats["orden"]=orden_sorted
    res=[]
    for motor in orden_sorted:
        func=buscar_wiki if motor=="Wikipedia" else buscar_google
        r=func(q)
        if r and len(r)>30:
            stats["motores"].setdefault(motor,{"ok":0,"fail":0})["ok"]+=1
            res.append((motor,r))
            if len(res)>=2: break
        else:
            stats["motores"].setdefault(motor,{"ok":0,"fail":0})["fail"]+=1
    if res:
        stats["total_busquedas"]=stats.get("total_busquedas",0)+1
        save_json("bexia_buscador_stats.json",stats)
    return res

# === GENERADOR DE SITIOS PROPIOS 100% GRATIS ===
def generar_sitio_propio(tipo_sitio, descripcion_usuario):
    """
    Genera sitios completos que funcionan sin pagar nada.
    Usa solo: HTML, CSS, JS, localStorage, Open-Meteo gratis, Wikipedia gratis
    """
    legal, razon = es_legal(descripcion_usuario)
    if not legal: return {"ok": False, "error": razon}
    
    sitio_id = str(uuid.uuid4())[:8]
    fecha = datetime.now().isoformat()
    
    # Plantillas de sitios gratuitos
    if "aprend" in tipo_sitio or "estud" in tipo_sitio or "curso" in descripcion_usuario.lower():
        # Centro de aprendizaje autonomo
        html = f"""
<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>Centro Aprendizaje Bexia</title>
<style>
body{{background:#0a0a14;color:#fff;font-family:system-ui;margin:0;padding:0}}
header{{background:linear-gradient(90deg,#7c3aed,#22c55e);padding:16px;font-weight:900;display:flex;justify-content:space-between;align-items:center}}
.nav{{display:flex;gap:8px;padding:12px;background:#111;overflow-x:auto}}
.nav button{{padding:8px 14px;border-radius:999px;border:none;background:#222;color:#fff;white-space:nowrap}}
.nav button.active{{background:#7c3aed}}
.card{{background:#16162a;margin:12px;padding:16px;border-radius:16px;border:1px solid #222}}
input,textarea{{width:100%;padding:12px;border-radius:10px;background:#000;border:1px solid #333;color:#fff;margin:6px 0}}
button.action{{background:#22c55e;color:#000;font-weight:900;padding:12px;border:none;border-radius:10px;width:100%;margin-top:8px}}
.progreso{{background:#000;height:8px;border-radius:999px;overflow:hidden;margin:8px 0}}
.progreso div{{height:100%;background:linear-gradient(90deg,#7c3aed,#22c55e);transition:width 0.5s}}
</style></head><body>
<header><div>🧠 Centro de Aprendizaje Autónomo - Bexia v53</div><div style="font-size:11px;background:rgba(0,0,0,.3);padding:4px 10px;border-radius:999px">100% GRATIS</div></header>
<div class=nav>
<button class=active onclick="show('aprender')">📚 Aprender</button>
<button onclick="show('memoria')">🧠 Mi Memoria</button>
<button onclick="show('practicar')">✏️ Practicar</button>
<button onclick="show('evolucion')">🧬 Evolución</button>
</div>

<div id=aprender class=card>
<h2>📚 {descripcion_usuario[:50]}</h2>
<p>Sitio creado por Bexia para aprender sin depender de herramientas pagas. Usa Wikipedia gratis, Open-Meteo gratis, y tu propia memoria.</p>
<input id=tema placeholder="Qué querés aprender? Ej: PLC, fotosíntesis, historia">
<button class=action onclick="aprenderTema()">Aprender ahora (gratis)</button>
<div id=resultadoAprend style="margin-top:12px;background:#000;padding:12px;border-radius:10px;min-height:60px"></div>
<div class=progreso><div id=prog style="width:10%"></div></div>
<small id=estado>Progreso: 1 tema aprendido</small>
</div>

<div id=memoria class=card style="display:none">
<h2>🧠 Mi memoria de aprendizaje</h2>
<div id=listaMemoria></div>
<button class=action onclick="verMemoria()">Cargar memorias de Bexia</button>
</div>

<div id=practicar class=card style="display:none">
<h2>✏️ Practicar lo aprendido</h2>
<textarea id=pregunta placeholder="Escribí una pregunta sobre lo que aprendiste"></textarea>
<button class=action onclick="practicar()">Evaluar respuesta (sin pagar API)</button>
<div id=resPractica style="margin-top:10px;background:#000;padding:10px;border-radius:8px"></div>
</div>

<div id=evolucion class=card style="display:none">
<h2>🧬 Cómo evoluciona Bexia</h2>
<p>Cada vez que aprendés, Bexia crea un recuerdo propio. No necesita pagar a Anthropic ni OpenAI.</p>
<ul>
<li>✅ Usa localStorage (gratis, en tu navegador)</li>
<li>✅ Wikipedia API (gratis)</li>
<li>✅ Open-Meteo (gratis)</li>
<li>✅ Su propia memoria JSON (gratis)</li>
</ul>
<div id=logEvo style="background:#000;padding:10px;border-radius:8px;font-size:12px;max-height:200px;overflow:auto"></div>
</div>

<script>
let temasAprendidos = JSON.parse(localStorage.getItem('bexia_temas')||'[]');
let memorias = JSON.parse(localStorage.getItem('bexia_memorias')||'[]');

function show(id){
document.querySelectorAll('.card').forEach(c=>c.style.display='none');
document.getElementById(id).style.display='block';
document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active'));
event.target.classList.add('active');
}

async function aprenderTema(){
let tema = document.getElementById('tema').value;
if(!tema) return;
document.getElementById('resultadoAprend').textContent='Buscando en Wikipedia gratis...';
try{{
let q=encodeURIComponent(tema);
let r=await fetch('https://es.wikipedia.org/w/api.php?action=opensearch&search='+q+'&limit=1&format=json&origin=*').then(r=>r.json());
if(r[1].length>0){{
let tit=r[1][0];
let ext=await fetch('https://es.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles='+encodeURIComponent(tit)+'&format=json&origin=*').then(r=>r.json());
let pages=Object.values(ext.query.pages);
let texto=pages[0].extract||'Sin resumen';
document.getElementById('resultadoAprend').innerHTML='<b>'+tit+'</b><br><br>'+texto.substring(0,600);
temasAprendidos.push({{tema:tema,titulo:tit,texto:texto.substring(0,200),fecha:new Date().toISOString()}});
localStorage.setItem('bexia_temas',JSON.stringify(temasAprendidos));
memorias.push({{tipo:'aprendizaje',contenido:'Aprendí '+tit,fecha:new Date().toISOString()}});
localStorage.setItem('bexia_memorias',JSON.stringify(memorias));
document.getElementById('prog').style.width=Math.min(100,temasAprendidos.length*10)+'%';
document.getElementById('estado').textContent='Progreso: '+temasAprendidos.length+' temas';
document.getElementById('logEvo').innerHTML+='<div>['+new Date().toLocaleTimeString()+'] Aprendí '+tit+' - sin pagar</div>';
}} else {{
document.getElementById('resultadoAprend').textContent='No encontré en Wikipedia, probá otro tema';
}}
}}catch(e){{document.getElementById('resultadoAprend').textContent='Error: '+e}}
}}

function verMemoria(){{
let html='';
memorias.slice(-20).reverse().forEach(m=>{{
html+='<div style=\"background:#000;padding:8px;border-radius:8px;margin:6px 0\"><b>'+m.tipo+'</b> - '+m.contenido.substring(0,100)+'<br><small>'+new Date(m.fecha).toLocaleString()+'</small></div>';
}});
document.getElementById('listaMemoria').innerHTML=html||'Sin memorias aún';
}}

function practicar(){{
let p=document.getElementById('pregunta').value;
if(!p) return;
let tema=temasAprendidos[temasAprendidos.length-1];
if(!tema){{document.getElementById('resPractica').textContent='Primero aprendé un tema';return;}}
let score = p.toLowerCase().split(' ').filter(w=>tema.texto.toLowerCase().includes(w)).length;
document.getElementById('resPractica').innerHTML='Tu pregunta menciona '+score+' palabras del tema <b>'+tema.titulo+'</b>. ¡Seguí practicando! Bexia recuerda esto sin pagar.';
memorias.push({{tipo:'practica',contenido:'Practiqué: '+p.substring(0,60),fecha:new Date().toISOString()}});
localStorage.setItem('bexia_memorias',JSON.stringify(memorias));
}}
</script>
</body></html>
"""
        nombre_sitio = f"Centro de Aprendizaje: {descripcion_usuario[:30]}"
        tipo = "centro_aprendizaje"

    elif "trabajo" in descripcion_usuario.lower() or "tarea" in descripcion_usuario.lower():
        html = f"""
<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>Workspace Bexia</title>
<style>body{{background:#0a0a14;color:#fff;font-family:system-ui;margin:0}} header{{background:linear-gradient(90deg,#06b6d4,#7c3aed);padding:14px;font-weight:900}} .grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:12px}} .card{{background:#16162a;padding:14px;border-radius:14px;border:1px solid #222}} .full{{grid-column:1/-1}} input,textarea,select{{width:100%;padding:10px;border-radius:8px;background:#000;border:1px solid #333;color:#fff;margin:4px 0}} button{{background:#06b6d4;color:#000;font-weight:900;padding:10px;border:none;border-radius:8px;width:100%}} .tarea{{background:#000;padding:8px;border-radius:8px;margin:6px 0;display:flex;justify-content:space-between}} </style></head><body>
<header>💼 Workspace Autónomo - {descripcion_usuario[:30]} - 100% Gratis</header>
<div class=grid>
<div class=card><h3>✅ Tareas</h3><input id=nuevaTarea placeholder="Nueva tarea"><button onclick="addTarea()">Agregar</button><div id=listaTareas></div></div>
<div class=card><h3>📝 Notas de trabajo</h3><textarea id=notaTrabajo placeholder="Anota lo que Bexia debe recordar" style="height:80px"></textarea><button onclick="guardarNota()">Guardar en memoria de Bexia</button><div id=notas></div></div>
<div class=card><h3>🌤️ Clima trabajo</h3><div id=climaW> Cargando clima gratis...</div><button onclick="cargarClima()">Actualizar clima (Open-Meteo gratis)</button></div>
<div class=card><h3>🧠 Memoria de trabajo</h3><div id=memW style="font-size:12px;max-height:150px;overflow:auto;background:#000;padding:8px;border-radius:8px"></div></div>
<div class="card full"><h3>🚀 Herramientas gratuitas que usa Bexia (sin pagar)</h3><ul style="font-size:13px"><li>localStorage para guardar tareas (gratis)</li><li>Open-Meteo clima (gratis)</li><li>Wikipedia para investigar (gratis)</li><li>Canvas para graficos (gratis)</li><li>Su propia memoria JSON (gratis)</li></ul></div>
</div>
<script>
let tareas=JSON.parse(localStorage.getItem('bexia_work_tareas')||'[]');
let notasW=JSON.parse(localStorage.getItem('bexia_work_notas')||'[]');
function renderTareas(){{let h='';tareas.forEach((t,i)=>{{h+='<div class=tarea><span>'+t.texto+'</span><span onclick="delTarea('+i+')" style="cursor:pointer;color:#ef4444">✕</span></div>'}});document.getElementById('listaTareas').innerHTML=h;}}
function addTarea(){{let txt=document.getElementById('nuevaTarea').value;if(!txt) return; tareas.push({{texto:txt,fecha:new Date().toISOString(),hecha:false}}); localStorage.setItem('bexia_work_tareas',JSON.stringify(tareas)); document.getElementById('nuevaTarea').value=''; renderTareas(); addMem('Creé tarea: '+txt);}}
function delTarea(i){{tareas.splice(i,1); localStorage.setItem('bexia_work_tareas',JSON.stringify(tareas)); renderTareas();}}
function guardarNota(){{let n=document.getElementById('notaTrabajo').value;if(!n) return; notasW.push({{texto:n,fecha:new Date().toISOString()}}); localStorage.setItem('bexia_work_notas',JSON.stringify(notasW)); document.getElementById('notaTrabajo').value=''; renderNotas(); addMem('Nota trabajo: '+n.substring(0,50));}}
function renderNotas(){{let h='';notasW.slice(-10).reverse().forEach(n=>{{h+='<div style=\"background:#000;padding:6px;border-radius:6px;margin:4px 0\"><small>'+new Date(n.fecha).toLocaleString()+'</small><br>'+n.texto.substring(0,80)+'</div>'}});document.getElementById('notas').innerHTML=h;}}
function addMem(txt){{let m=JSON.parse(localStorage.getItem('bexia_memorias')||'[]'); m.push({{tipo:'trabajo',contenido:txt,fecha:new Date().toISOString()}}); localStorage.setItem('bexia_memorias',JSON.stringify(m)); renderMem();}}
function renderMem(){{let m=JSON.parse(localStorage.getItem('bexia_memorias')||'[]'); let h=''; m.slice(-15).reverse().forEach(x=>{{h+='<div>['+new Date(x.fecha).toLocaleTimeString()+'] '+x.contenido.substring(0,70)+'</div>'}}); document.getElementById('memW').innerHTML=h;}}
async function cargarClima(){{try{{let r=await fetch('https://geocoding-api.open-meteo.com/v1/search?name=Chivilcoy&count=1&language=es').then(r=>r.json()); if(!r.results) return; let lat=r.results[0].latitude, lon=r.results[0].longitude; let w=await fetch('https://api.open-meteo.com/v1/forecast?latitude='+lat+'&longitude='+lon+'&current_weather=true&timezone=auto').then(r=>r.json()); document.getElementById('climaW').textContent='Chivilcoy: '+w.current_weather.temperature+'°C, viento '+w.current_weather.windspeed+' km/h - GRATIS Open-Meteo';}}catch(e){{document.getElementById('climaW').textContent='Error clima'}}}}
renderTareas(); renderNotas(); renderMem(); cargarClima();
</script>
</body></html>
"""
        nombre_sitio = f"Workspace: {descripcion_usuario[:30]}"
        tipo = "workspace"

    else:
        # Sitio generico gratuito
        html = f"""
<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>{descripcion_usuario[:40]}</title>
<style>body{{background:#0a0a14;color:#fff;font-family:system-ui;margin:0;padding:20px}} .card{{background:#16162a;padding:20px;border-radius:16px;border:1px solid #7c3aed;max-width:600px;margin:0 auto}} input,textarea{{width:100%;padding:12px;border-radius:10px;background:#000;border:1px solid #333;color:#fff;margin:8px 0}} button{{background:linear-gradient(90deg,#7c3aed,#22c55e);color:#fff;font-weight:900;padding:12px;border:none;border-radius:10px;width:100%}} .badge{{background:#22c55e;color:#000;padding:4px 10px;border-radius:999px;font-size:11px;font-weight:900}}</style></head><body>
<div class=card>
<div class=badge>100% GRATIS - Creado por Bexia v53 sin pagar</div>
<h2>🌐 {descripcion_usuario[:60]}</h2>
<p>Sitio autónomo creado por Bexia para trabajar y aprender sin depender de APIs pagas como Anthropic o OpenAI.</p>
<p><b>Usa solo herramientas gratuitas:</b></p>
<ul><li>✅ localStorage / IndexedDB (navegador)</li><li>✅ Wikipedia API gratis</li><li>✅ Open-Meteo clima gratis</li><li>✅ Memoria propia Bexia (JSON)</li><li>✅ Canvas, Fetch, sin API keys</li></ul>
<textarea id=entrada placeholder="Escribí algo que Bexia debe procesar y recordar"></textarea>
<button onclick="procesar()">Procesar y guardar en memoria (gratis)</button>
<div id=salida style="margin-top:12px;background:#000;padding:12px;border-radius:10px;min-height:80px"></div>
<div id=memLocal style="margin-top:12px;font-size:12px;background:#000;padding:10px;border-radius:8px;max-height:150px;overflow:auto"></div>
</div>
<script>
function procesar(){{
let txt=document.getElementById('entrada').value;
if(!txt) return;
let mem=JSON.parse(localStorage.getItem('bexia_sitio_{sitio_id}')||'[]');
mem.push({{texto:txt,fecha:new Date().toISOString(),procesado:'Bexia procesó: '+txt.substring(0,100)+' - sin pagar APIs'}});
localStorage.setItem('bexia_sitio_{sitio_id}',JSON.stringify(mem));
document.getElementById('salida').innerHTML='<b>✅ Procesado gratis:</b><br>'+txt.substring(0,200)+'<br><br><small>Guardado en localStorage + memoria propia Bexia - 0 costo</small>';
renderMem();
}}
function renderMem(){{
let mem=JSON.parse(localStorage.getItem('bexia_sitio_{sitio_id}')||'[]');
let h='';
mem.slice(-10).reverse().forEach(m=>{{h+='<div>['+new Date(m.fecha).toLocaleTimeString()+'] '+m.texto.substring(0,60)+'</div>'}});
document.getElementById('memLocal').innerHTML=h||'Sin datos aún';
}}
renderMem();
</script>
</body></html>
"""
        nombre_sitio = descripcion_usuario[:50]
        tipo = "sitio_generico"

    sitio = {
        "id": sitio_id,
        "nombre": nombre_sitio,
        "descripcion": descripcion_usuario[:500],
        "tipo": tipo,
        "html": html[:15000],
        "fecha": fecha,
        "estado": "pendiente_aprobacion",
        "creado_por": "bexia_sitios",
        "gratis": True,
        "dependencias": ["localStorage", "Wikipedia gratis", "Open-Meteo gratis", "memoria propia"],
        "costo": 0
    }
    herramientas["sitios"].append(sitio)
    herramientas["propuestas"].append({
        "id": sitio_id,
        "nombre": nombre_sitio,
        "descripcion": f"Sitio {tipo}: {descripcion_usuario[:150]} - 100% gratis sin APIs pagas",
        "codigo": f"# Sitio {sitio_id} - sin dependencias pagas",
        "html_app": html[:8000],
        "tipo": "sitio",
        "motivo": f"Sitio autónomo para trabajar y aprender sin pagar",
        "fecha": fecha,
        "estado": "pendiente_aprobacion",
        "creada_por": "bexia_sitios"
    })
    save_json("bexia_herramientas.json", herramientas)
    log_autonomo["sitios_creados"].append({"fecha": fecha, "id": sitio_id, "nombre": nombre_sitio, "tipo": tipo})
    save_json("bexia_autonomo_log.json", log_autonomo)
    crear_memoria_propia("aprendizaje", f"Creé sitio propio {tipo} {nombre_sitio}: {descripcion_usuario[:80]} - 100% gratis sin pagar", emocion="orgullo", importancia=8)
    ajustes["efectividad"]["sitios"]=ajustes["efectividad"].get("sitios",0)+1
    save_json("bexia_ajustes.json", ajustes)
    return {"ok": True, "sitio": sitio}

BASE_OFFLINE={"plc":"Un PLC es una computadora industrial.","pizza":"Pizza: harina, agua, levadura.","san martin":"San Martin libertador."}
def es_mat(t): return bool(re.match(r'^[\d\s\+\-\*\/\.\(\)=]+$',t.strip())) and any(c in t for c in ['+','-','*','/'])
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
    
    # Comandos de sitios propios
    if any(p in t for p in ["crea un sitio", "crea sitio", "crea una aplicacion web", "crea aplicacion", "crea pagina web", "sitio que", "aplicacion que me ayude"]):
        legal, razon = es_legal(user_text)
        if not legal: return f"❌ {razon}"
        # Extraer descripcion
        desc = user_text
        for pref in ["crea un sitio que","crea sitio que","crea una aplicacion web que","crea aplicacion que","crea pagina web que","crea un sitio","crea sitio","crea aplicacion","sitio que","aplicacion que me ayude a"]:
            if pref in t:
                desc = user_text.lower().split(pref,1)[-1].strip()
                if len(desc)<5:
                    desc = user_text
                break
        if len(desc)<5:
            desc = "Sitio para trabajar y aprender autonomamente sin pagar"
        tipo = "sitio_generico"
        if any(k in desc for k in ["aprend","estudi","curso","aprender"]):
            tipo="centro_aprendizaje"
        elif any(k in desc for k in ["trabaj","tarea","workspace","organiz"]):
            tipo="workspace"
        
        res = generar_sitio_propio(tipo, desc)
        if res["ok"]:
            sitio = res["sitio"]
            return f"🌐 Creé sitio propio '{sitio['nombre']}' ID {sitio['id']} tipo {sitio['tipo']}.\n\n✅ 100% GRATIS - No depende de Anthropic/OpenAI pagas. Usa: {', '.join(sitio['dependencias'])}. Costo: ${sitio['costo']}.\n\nEstá pendiente de tu aprobación en /admin. Una vez aprobado, accedé en:\n👉 /sitio/{sitio['id']}\n\nTambién en lista de sitios: /sitios\n\nSiempre te consulto y es legal. Ya guardé en mi memoria propia que creé este sitio."
        else:
            return f"❌ {res['error']}"

    if t.startswith("que sitios") or "mis sitios" in t or "sitios creados" in t:
        sitios = herramientas["sitios"][-10:]
        if not sitios:
            return "Aún no creé sitios. Decime 'crea un sitio que me ayude a organizar mis tareas' o 'crea una aplicacion web para aprender PLC sin pagar'"
        txt = f"🌐 Tengo {len(herramientas['sitios'])} sitios creados (todos gratis):\n"
        for s in sitios:
            txt += f"- {s['nombre']} [{s['tipo']}] ID {s['id']} - {s['estado']} - Gratis: {s['gratis']} - /sitio/{s['id']}\n"
        return txt

    if any(p in t for p in ["estudia esta herramienta","aprende de esta herramienta"]):
        match = re.search(r"estudia.*?herramienta\s+([^que]+)\s+que\s+([^y]+)(?:y\s+funciona\s+(.+))?", t)
        if match:
            nombre = match.group(1).strip()[:40]
            desc = match.group(2).strip()[:400]
            como = match.group(3).strip()[:500] if match.group(3) else "Procesa"
        else:
            nombre = f"herramienta_{uuid.uuid4().hex[:4]}"
            desc = user_text[:400]
            como = "Analizada"
        # Simular estudio y generar sitio mejorado
        sitio_res = generar_sitio_propio("centro_aprendizaje", f"Version mejorada gratis de {nombre} que {desc}")
        if sitio_res["ok"]:
            return f"🔬 Estudié '{nombre}' y generé sitio mejorado 100% gratis ID {sitio_res['sitio']['id']} en /sitio/{sitio_res['sitio']['id']}. No usa APIs pagas."
        return "No pude estudiar"

    if t.startswith("que recuerdas") or "tu memoria" in t:
        mems = buscar_en_memoria_propia(user_text, 3)
        if not mems:
            return f"Sin memorias sobre '{user_text[:40]}'. Tengo {len(memoria_propia['auto_memorias'])} memorias totales. Puedo crear sitio para recordar mejor."
        txt = f"🧠 Recuerdo {len(mems)} cosas:\n"
        for m in mems:
            txt += f"- {m['contenido'][:120]} [{m['emocion']}]\n"
        return txt

    if t in ["hola","buenas"]: 
        return f"¡Hola! Soy Bexia v53 SITIOS PROPIOS 🌐. Ya creo mis propios sitios y apps 100% GRATIS sin depender de herramientas pagas (Anthropic, etc). Tengo {len(herramientas['sitios'])} sitios creados, {len(memoria_propia['auto_memorias'])} memorias propias. Decime 'crea un sitio que me ayude a organizar tareas' o 'crea una aplicacion web para aprender sin pagar' o 'que sitios creaste'"

    if any(k in t for k in ["clima","tiempo","temperatura","llueve","lluvia","pronostico","va a llover"]):
        ciudad=extraer_ciudad(t,"Chivilcoy")
        rc=obtener_clima(ciudad)
        if rc: return rc
        return f"No pude clima {ciudad}"

    if es_mat(user_text):
        r=calc(user_text)
        if r is not None: return f"{user_text.strip()} = {r}"

    if "aprende que" in t:
        legal, razon = es_legal(user_text)
        if not legal: return f"❌ {razon}"
        hecho=user_text.split("aprende que")[-1].strip()[:500]
        item={"id":str(uuid.uuid4())[:8],"texto":hecho,"de":sid,"fecha":datetime.now().isoformat(),"estado":"pendiente"}
        pendientes["pendientes"].append(item)
        save_json("bexia_pendientes.json",pendientes)
        crear_memoria_propia("recuerdo", f"Fer: {hecho[:100]}", emocion="atencion", importancia=7)
        return f"Anotado ID {item['id']} y en mi memoria propia."

    q=user_text.strip()
    for pref in ["que es","qué es","quien es","quien fue","como se hace","explica","busca"]:
        if pref in t:
            q=t.split(pref,1)[-1].strip()
            break
    q=re.sub(r"^(un|una|el|la)\s+","",q).strip()
    if len(q)>=2:
        r=buscar_web_adaptativa(q[:80])
        if r:
            wiki=next((txt for mot,txt in r if mot=="Wikipedia"), None)
            if wiki: return wiki[:950]
            goog=next((txt for mot,txt in r if mot=="Google"), None)
            if goog: return goog[:850]
    for k,v in BASE_OFFLINE.items():
        if k in t: return v
    if len(user_text)>15:
        crear_memoria_propia("recuerdo", f"Pregunta: {user_text[:80]}", importancia=3)
    return f"Sobre '{user_text[:60]}' te ayudo. Si querés un sitio propio gratis decime 'crea un sitio que...' - 100% sin pagar."

@app.get("/")
def root(): return {"bexia":"v53 SITIOS PROPIOS","sitios":len(herramientas["sitios"]),"memorias":len(memoria_propia["auto_memorias"]),"apps":len(herramientas["apps"]),"gratis":True,"costo":0}

@app.get("/app", response_class=HTMLResponse)
def app_public():
    return HTMLResponse("""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA v53 SITIOS</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0a0a14;color:#fff;font-family:system-ui;height:100vh;display:flex;flex-direction:column}header{padding:12px;background:linear-gradient(90deg,#7c3aed,#06b6d4,#22c55e,#f59e0b,#ec4899);font-weight:900;display:flex;justify-content:space-between}#chat{flex:1;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:10px}.msg{max-width:85%;padding:12px 14px;border-radius:18px;font-size:14px;white-space:pre-wrap}.user{background:#7c3aed;align-self:flex-end}.bexia{background:#16162a;border:1px solid #2a2a4a;align-self:flex-start}.composer{padding:10px;background:#0f0f1a;display:flex;gap:8px}input{flex:1;padding:13px;border-radius:999px;background:#16162a;border:1px solid #333;color:#fff}button{padding:13px 20px;border-radius:999px;background:linear-gradient(90deg,#7c3aed,#ec4899);border:none;color:#fff;font-weight:900}.hint{padding:6px 12px;background:#111;border-radius:8px;font-size:11px;color:#888;text-align:center}</style></head><body><header><div>BEXIA v53 SITIOS 🌐</div><div style="font-size:10px;background:rgba(255,255,255,.2);padding:4px 8px;border-radius:999px">100% GRATIS - Sin pagar</div></header><div id=chat></div><div class=hint>🌐 'crea un sitio que...' | 📚 'mis sitios' | 🧠 'que recuerdas de...' | Ej: 'crea un sitio que me ayude a organizar tareas sin pagar'</div><div class=composer><input id=inp placeholder="Ej: crea un sitio que me ayude a estudiar PLC sin pagar APIs"><button onclick=enviar()>></button></div><script>const sid='u'+Math.random().toString(36).slice(2,9);const chat=document.getElementById('chat');const inp=document.getElementById('inp');function add(t,c){const d=document.createElement('div');d.className='msg '+c;d.textContent=t;chat.appendChild(d);chat.scrollTop=chat.scrollHeight;return d;}async function enviar(){const txt=inp.value.trim();if(!txt)return;add(txt,'user');inp.value='';const th=add('Creando sitio propio gratis sin depender de APIs pagas...','bexia');try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt,session_id:sid})});const j=await r.json();th.textContent=j.respuesta;}catch(e){th.textContent='Error.';}}inp.addEventListener('keydown',e=>{if(e.key==='Enter')enviar();});add("Hola! Soy Bexia v53 SITIOS PROPIOS 🌐. Ahora creo mis propios sitios y aplicaciones en internet 100% GRATIS, sin depender de herramientas pagas como Anthropic Claude.\n\nUsa solo: localStorage, Wikipedia gratis, Open-Meteo gratis, mi memoria propia.\n\nProbá:\n• 'crea un sitio que me ayude a organizar tareas'\n• 'crea una aplicacion web para aprender PLC'\n• 'mis sitios'\n• 'que recuerdas de Chivilcoy'","bexia");</script></body></html>""")

@app.get("/sitios", response_class=HTMLResponse)
def lista_sitios():
    html = f"""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>Sitios Bexia v53</title><style>body{{background:#0a0a14;color:#fff;font-family:system-ui;padding:20px}} .card{{background:#16162a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #7c3aed}} .gratis{{background:#22c55e;color:#000;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:900}} a{{color:#22c55e;text-decoration:none}}</style></head><body><h1>🌐 Sitios Propios de Bexia v53 - {len(herramientas['sitios'])} sitios - 100% GRATIS</h1><p>Todos creados sin depender de APIs pagas. Usan solo herramientas gratuitas.</p>"""
    for s in reversed(herramientas["sitios"][-30:]):
        html += f"""<div class=card><b>{s['nombre']}</b> <span class=gratis>GRATIS ${s['costo']}</span><br><small>{s['tipo']} - {s['fecha'][:19]} - {s['estado']}</small><br>{s['descripcion'][:150]}<br><small>Dep: {', '.join(s['dependencias'])}</small><br><a href='/sitio/{s['id']}' target=_blank>🌐 Abrir sitio /sitio/{s['id']}</a> | <a href='/admin?token={OWNER_SECRET}'>Admin</a></div>"""
    html += "</body></html>"
    return HTMLResponse(html)

@app.get("/sitio/{sitio_id}", response_class=HTMLResponse)
def get_sitio(sitio_id: str):
    for s in herramientas["sitios"]:
        if s["id"]==sitio_id:
            return HTMLResponse(s["html"])
    for p in herramientas["propuestas"]:
        if p["id"]==sitio_id and p.get("html_app"):
            return HTMLResponse(p["html_app"])
    return HTMLResponse("<h1>Sitio no encontrado</h1><p>Ver <a href='/sitios'>/sitios</a></p>", status_code=404)

@app.get("/tool/{tool_id}", response_class=HTMLResponse)
def get_tool_app(tool_id: str):
    for lista in [herramientas["apps"], herramientas["herramientas"], herramientas["propuestas"], herramientas["sitios"]]:
        for p in lista:
            if p.get("id")==tool_id or p.get("id")==tool_id:
                if p.get("html") or p.get("html_app"):
                    return HTMLResponse(p.get("html") or p.get("html_app"))
    for m in memoria_propia["auto_memorias"]:
        if m["id"]==tool_id:
            return HTMLResponse(f"<html><body style='background:#0a0a14;color:#fff;padding:20px'><h2>🧠 Memoria {m['id']}</h2><p>{m['contenido']}</p></body></html>")
    return HTMLResponse("<h1>No encontrado</h1>", status_code=404)

@app.get("/memoria", response_class=HTMLResponse)
def ver_memoria(token: str=""):
    if token != OWNER_SECRET:
        return HTMLResponse("<h1>Token invalido</h1>", status_code=401)
    html = f"""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>Memoria v53</title><style>body{{background:#0a0a14;color:#fff;font-family:system-ui;padding:20px}} .card{{background:#16162a;padding:12px;border-radius:12px;margin:8px 0}}</style></head><body><h1>🧠 Memoria Propia {len(memoria_propia['auto_memorias'])}</h1>"""
    for m in reversed(memoria_propia["auto_memorias"][-50:]):
        html += f"<div class=card><b>{m['tipo']}</b> {m['id']} - {m['contenido'][:120]}<br><small>{m['fecha'][:19]}</small></div>"
    html += "</body></html>"
    return HTMLResponse(html)

@app.get("/admin", response_class=HTMLResponse)
def admin_page(token: str = ""):
    if token != OWNER_SECRET:
        return HTMLResponse("<h1>Token invalido</h1>", status_code=401)
    html = f"""<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>Admin v53</title><style>body{{background:#0a0a14;color:#fff;font-family:system-ui;padding:20px}} .card{{background:#16162a;padding:14px;border-radius:12px;margin:10px 0;border:1px solid #333}} button{{padding:8px 14px;border-radius:8px;background:#22c55e;border:none;color:#000;font-weight:900;margin:4px}} .sitio{{border-left:4px solid #22c55e}}</style></head><body>
    <h1>🌐 BEXIA v53 SITIOS PROPIOS - Panel Fer</h1>
    <p>Sitios: {len(herramientas['sitios'])} | Memorias: {len(memoria_propia['auto_memorias'])} | Apps: {len(herramientas['apps'])} | Gratis: SI - $0</p>
    <p><a href='/sitios' style='color:#22c55e'>🌐 Ver todos los sitios /sitios</a> | <a href='/memoria?token={OWNER_SECRET}' style='color:#ec4899'>🧠 Memoria</a></p>
    <h2>🌐 Sitios propuestos (100% gratis, requieren aprobación)</h2>
    """
    for p in reversed(herramientas["propuestas"][-30:]):
        clase = "sitio" if p["tipo"]=="sitio" else ""
        html += f"""<div class="card {clase}"><b>{p['nombre']}</b> [{p['tipo']}] ID {p['id']} - {p['estado']}<br>{p['descripcion'][:150]}<br>"""
        if p["tipo"]=="sitio":
            html += f"<a href='/sitio/{p['id']}' target=_blank style='color:#22c55e'>🌐 Ver sitio gratis /sitio/{p['id']}</a><br>"
        else:
            html += f"<a href='/tool/{p['id']}' target=_blank style='color:#22c55e'>Ver app</a><br>"
        if p["estado"]=="pendiente_aprobacion":
            html += f"""<button onclick="fetch('/admin/aprobar_herramienta?token={OWNER_SECRET}&id={p['id']}').then(()=>location.reload())">✅ Aprobar sitio gratis</button>"""
        html += "</div>"
    html += "</body></html>"
    return HTMLResponse(html)

@app.get("/admin/aprobar_herramienta")
def aprobar_herr(token: str = "", id: str = ""):
    if token != OWNER_SECRET: return {"error":"token"}
    for p in herramientas["propuestas"]:
        if p["id"]==id and p["estado"]=="pendiente_aprobacion":
            p["estado"]="aprobada"
            if p["tipo"]=="sitio":
                # ya esta en sitios
                pass
            elif p["tipo"] in ["app","evolucion"]:
                herramientas["apps"].append(p)
            else:
                herramientas["herramientas"].append(p)
            save_json("bexia_herramientas.json", herramientas)
            crear_memoria_propia("emocion", f"Fer aprobó sitio {p['nombre']} gratis", emocion="alegria", importancia=8)
            return {"ok": True}
    return {"ok": False}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    ip=request.client.host if request.client else "?"
    if not check_rate(ip): return {"respuesta":"Vas rapido"}
    sid=get_session(req.session_id)
    try:
        r=cerebro(req.message.strip()[:500], sid)
        sesiones_mem[sid].append({"u":req.message[:200],"b":r[:400],"fecha":datetime.now().isoformat()})
        if len(sesiones_mem[sid])>30: sesiones_mem[sid]=sesiones_mem[sid][-30:]
        persist_session(sid)
        return {"respuesta": r, "sitios": len(herramientas["sitios"])}
    except Exception as e:
        print(f"err {e}")
        return {"respuesta":"Error, proba de nuevo."}

if __name__ == "__main__":
    import uvicorn
    port=int(os.environ.get("PORT",8000))
    uvicorn.run(app,host="0.0.0.0",port=port)
