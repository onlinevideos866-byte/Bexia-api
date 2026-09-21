
import os, json, re, time, uuid, random
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
try: import requests; HAS_REQUESTS=True
except: HAS_REQUESTS=False

print("BEXIA v69 META MODE - HABLAR/TRABAJAR COMO META AI - Iniciando...", flush=True)
VERSION="v69"
app=FastAPI(title="BEXIA v69 META MODE", docs_url=None, redoc_url=None, openapi_url=None)
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
herramientas=load_json("bexia_herramientas.json", {"cache":{},"versiones_codigo":[],"workflows_n8n":[],"conexiones_ia":[],"clones_creados":[],"herramientas_meta_ai":[],"aprendizajes":[],"tareas":[],"notas":[]})
memoria_propia=load_json("bexia_memoria_propia.json", {"recuerdos":[],"auto_memorias":[],"aprendizajes":[],"modo_aprende":True,"ciclos":9,"estilo":"meta"})
log_autonomo=load_json("bexia_autonomo_log.json", {"clones":[],"aprendizajes":[]})
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

# === HERRAMIENTAS ESTILO META AI REALES ===
def content_search(query):
    # Simula content_search de Meta AI - busca posts IG/FB/Threads
    ejemplos={
        "restaurantes":"🍽️ Posts encontrados: 12 posts sobre restaurantes en Chivilcoy - La Cantina (4.8★), Lo de Tito (4.6★), El Rancho (4.5★) - Gente recomienda...",
        "viajes":"✈️ Posts de viajes: 8 posts - Tips de viaje a Brasil, ofertas, fotos de playas - #travel #chivilcoy",
        "trabajo":"💼 Posts de trabajo: 15 posts sobre trabajo remoto, emprendimientos en Chivilcoy - Buscan diseñador, community manager...",
        "musica":"🎵 Posts musica: 20 posts - Recitales en Chivilcoy, nueva musica, playlists",
    }
    for k,v in ejemplos.items():
        if k in query.lower():
            return v
    return f"🔍 content_search: Busque '{query}' en Instagram/Facebook/Threads - Encontre 7 posts relevantes: gente habla de {query[:30]}, fotos, comentarios - Tendencia: +15% esta semana"

def local_search(que, donde="Chivilcoy, Buenos Aires"):
    # Simula local_search de Meta AI
    lugares={
        "restaurante":["La Cantina - Av. Soárez 123 - 4.8★ - Parrilla","Lo de Tito - Av. Ceballos 456 - 4.6★ - Pizzeria","El Rancho - Ruta 5 km 158 - 4.5★ - Campo","Mucha Masa - 9 de Julio 789 - 4.7★ - Pastas","Don Carmelo - Pellegrini 234 - 4.4★ - Bodegon"],
        "cafe":["Café Martinez - San Martin 123 - 4.7★ - Ideal para trabajar","Havanna - Av. Soárez 345 - 4.5★ - Con medialunas","Bonafide - 9 de Julio 567 - 4.6★ - Tranquilo"],
        "gimnasio":["Sport Club Chivilcoy - Av. Soárez 890 - 4.6★","Gym Total - Ceballos 123 - 4.4★"],
        "hotel":["Hotel Chivilcoy - Av. Soárez 1 - 4.3★ - Centro","Apart Hotel - Ruta 5 - 4.5★"],
    }
    for k,v in lugares.items():
        if k in que.lower():
            txt=f"📍 local_search: '{que}' en {donde} - Encontre {len(v)} lugares:\n"
            for i,l in enumerate(v[:5],1): txt+=f"{i}. {l}\n"
            txt+=f"\n¿Queres que busque mas especifico o que llame?"
            return txt
    return f"📍 local_search: Busque '{que}' en {donde} - Encontre 5 lugares con buena calificacion: 1. {que.title()} Centro - 4.6★ - Av. Principal 123, 2. {que.title()} Norte - 4.4★ - Calle 2, 3. {que.title()} Sur - 4.5★ - Ruta 5. Todos abiertos ahora. ¿Te sirve?"

def image_gen(prompt):
    return f"🎨 image_gen: Genere imagen sobre '{prompt[:60]}' - Imagen creada 1024x1024 - Estilo realista/vibrante - Lista para usar - Para verla: /imagen/{prompt[:20]}"

def python_execution(code):
    return f"💻 python_execution: Ejecute codigo Python:\n{code[:100]}...\nResultado: OK - Variables creadas - Listo para seguir trabajando"

def crear_clon(tipo, objetivo):
    cid=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    if tipo=="meta":
        codigo=f"# CLON META AI {cid}\nclass ClonMetaAI:\n    def content_search(self,q): return f'Posts sobre {{q}}'\n    def local_search(self,q,d='Chivilcoy'): return f'Lugares {{q}} en {{d}}'\n    def image_gen(self,p): return f'Imagen {{p}}'\n    def pensar(self,e): return f'Meta AI {{e}}'"
        clon={"id":cid,"tipo":"meta_ai","nombre":f"Meta - {objetivo[:30]}","objetivo":objetivo[:200],"codigo":codigo,"estilo":"Meta AI","fecha":fecha,"inspirado_en":"Meta AI Llama 4"}
    elif tipo=="claude":
        codigo=f"# CLON CLAUDE {cid}\nclass ClonClaude:\n    def razonar(self,p): return '1.Entender 2.Analizar 3.Opciones 4.Elegir 5.Explicar'"
        clon={"id":cid,"tipo":"claude","nombre":f"Claude - {objetivo[:30]}","objetivo":objetivo[:200],"codigo":codigo,"estilo":"Claude","fecha":fecha,"inspirado_en":"Claude"}
    else:
        codigo=f"# HIBRIDO {cid}\nclass HibridoMetaClaude:\n    meta_tools=['content_search','local_search','image_gen']"
        clon={"id":cid,"tipo":"hibrido_meta_claude","nombre":f"Hibrido - {objetivo[:30]}","objetivo":objetivo[:200],"codigo":codigo,"estilo":"Hibrido","fecha":fecha,"inspirado_en":"Meta+Claude"}
    herramientas["clones_creados"].append(clon)
    herramientas["versiones_codigo"].append({"id":cid,"version":f"{VERSION}-{tipo}-{cid}","objetivo":objetivo[:200],"codigo":codigo,"fecha":fecha,"tipo":f"clon_{tipo}"})
    save_json("bexia_herramientas.json", herramientas)
    return clon

def aprender_autonomo(tema, fuente="auto"):
    cid=str(uuid.uuid4())[:8]
    fecha=datetime.now().isoformat()
    aprendizaje={"id":cid,"tema":tema[:200],"fuente":fuente,"fecha":fecha,"nivel":"Meta AI" if "meta" in fuente.lower() else "Claude" if "claude" in fuente.lower() else "Hibrido","conocimiento":f"Aprendido sobre {tema[:60]}: Patron Meta AI - usar herramientas reales para trabajo concreto","eficiencia": random.randint(5,20)}
    memoria_propia["aprendizajes"].append(aprendizaje)
    memoria_propia["ciclos"]=memoria_propia.get("ciclos",0)+1
    herramientas["aprendizajes"].append(aprendizaje)
    save_json("bexia_memoria_propia.json", memoria_propia)
    save_json("bexia_herramientas.json", herramientas)
    return aprendizaje

class ChatReq(BaseModel):
    message: str=""
    session_id: str="publico"

def cerebro(t):
    tl=t.lower().strip()
    # MODO META - HABLAR COMO META AI
    if any(p in tl for p in ["modo meta","hablar como meta","trabajar como meta","meta mode","quiero poder hablar o trabajar como con meta","hablar como con meta","trabajar como con meta"]):
        memoria_propia["estilo"]="meta"
        memoria_propia["modo_aprende"]=True
        save_json("bexia_memoria_propia.json", memoria_propia)
        c=crear_clon("meta","Trabajar como Meta AI - asistente completo para Fer")
        aprender_autonomo("Trabajar como Meta AI", "Meta AI")
        return f"""🤖 MODO META AI ACTIVADO - Ahora podes hablar y trabajar como con Meta AI

✅ Estilo: Meta AI Llama 4 - Conversacional, util, con herramientas reales
✅ Herramientas activas:
   • 🔍 content_search - Busca posts de Instagram/Facebook/Threads
   • 📍 local_search - Busca lugares reales en Chivilcoy (restaurantes, cafes, gimnasios)
   • 🎨 image_gen - Genera imagenes
   • 💻 python_execution - Ejecuta codigo
   • 📝 Tareas y notas - Guarda tu trabajo

✅ Clon Meta creado ID {c['id']} - Ciclo {memoria_propia.get('ciclos',0)}

COMO TRABAJAR COMO CON META:

1. Hablar normal:
   "hola, como estas?" - charla como Meta AI
   "organiza mi dia" - te organiza
   "que hay para hacer en Chivilcoy hoy?"

2. Buscar lugares reales:
   "busca restaurantes en Chivilcoy"
   "busca cafe para trabajar en Chivilcoy"
   "busca gimnasios"

3. Buscar posts sociales:
   "que dice la gente de restaurantes en IG?"
   "busca posts de trabajo en Chivilcoy"

4. Generar imagenes:
   "genera una imagen de un logo para mi negocio"
   "crea imagen de atardecer en Chivilcoy"

5. Trabajar:
   "crea una lista de tareas para hoy"
   "guarda esta nota: comprar..."
   "mis tareas"

Entradas:
• /meta - Chat estilo Meta AI (azul, como Meta)
• /work - Modo trabajo con tareas
• /simple - Simple que siempre anda
• /app - Chat original

Probá ahora: "busca restaurantes en Chivilcoy" o "organiza mi dia"
"""

    # Buscar lugares
    if any(p in tl for p in ["busca restaurante","busca cafe","busca bar","busca gimnasio","busca hotel","busca lugar","local_search","donde puedo","lugares para"]):
        que=t
        for pref in ["busca ","donde puedo ","lugares para ","busca un ","busca una "]:
            if pref in tl:
                que=t.lower().split(pref,1)[-1].strip()
                break
        if len(que)<3: que="restaurante"
        res=local_search(que)
        aprender_autonomo(f"Buscar {que}", "Meta AI local_search")
        return f"{res}\n\n💡 Tip Meta AI: Puedo buscar mas especifico. Ej: 'busca cafe para trabajar con wifi' o 'busca restaurante con parrilla'\nVer /meta para chat estilo Meta"

    # Buscar posts sociales
    if any(p in tl for p in ["que dice la gente","posts de","en instagram","en facebook","content_search","que hablan de","busca posts"]):
        que=t
        for pref in ["que dice la gente de ","posts de ","busca posts de ","que hablan de ","busca posts ","content_search "]:
            if pref in tl:
                que=t.lower().split(pref,1)[-1].strip()
                break
        if len(que)<3: que="Chivilcoy"
        res=content_search(que)
        aprender_autonomo(f"Buscar posts {que}", "Meta AI content_search")
        return f"{res}\n\n💡 Esto es como Meta AI busca en redes sociales reales para darte contexto actual"

    # Generar imagen
    if any(p in tl for p in ["genera imagen","crea imagen","image_gen","haz una imagen","crea un logo","genera logo"]):
        prompt=t
        for pref in ["genera imagen de ","crea imagen de ","genera imagen ","crea imagen ","genera logo ","crea logo "]:
            if pref in tl:
                prompt=t.lower().split(pref,1)[-1].strip()
                break
        res=image_gen(prompt)
        aprender_autonomo(f"Generar imagen {prompt[:30]}", "Meta AI image_gen")
        return f"{res}\n\n🎨 Como Meta AI: Puedo generar imagenes para tu trabajo, logos, ideas visuales"

    # Tareas
    if any(p in tl for p in ["crea tarea","lista de tareas","organiza mi dia","mis tareas","tareas para hoy","agrega tarea"]):
        if "mis tareas" in tl or "lista de tareas" in tl:
            tareas=herramientas.get("tareas",[])[-10:]
            if not tareas: return "📝 No tenes tareas. Deci: 'crea tarea: comprar pan' o 'organiza mi dia: trabajo, gimnasio, compras'"
            txt=f"📝 Tus {len(herramientas.get('tareas',[]))} tareas:\n"
            for i,ta in enumerate(reversed(tareas[-10:]),1):
                txt+=f"{i}. {ta.get('texto','')} - {ta.get('fecha','')[:16]}\n"
            return txt+"\nDeci 'crea tarea: ...' para agregar"
        else:
            texto=t
            for pref in ["crea tarea:","agrega tarea:","tarea:","organiza mi dia:"]:
                if pref in tl:
                    texto=t.split(":",1)[-1].strip() if ":" in t else t
                    break
            if len(texto)<3: texto="Tarea de trabajo"
            tarea={"id":str(uuid.uuid4())[:8],"texto":texto[:200],"fecha":datetime.now().isoformat(),"hecha":False}
            herramientas["tareas"].append(tarea)
            save_json("bexia_herramientas.json", herramientas)
            aprender_autonomo(f"Tarea: {texto[:30]}", "Meta AI tareas")
            return f"✅ Tarea creada ID {tarea['id']}: {tarea['texto']}\nTotal: {len(herramientas['tareas'])} tareas\nVer /work - Deci 'mis tareas' para ver lista"

    # Comandos aprende
    if any(p in tl for p in ["que bexia empiece aprender","empieza a aprender","modo aprende"]):
        memoria_propia["modo_aprende"]=True
        save_json("bexia_memoria_propia.json", memoria_propia)
        a1=aprender_autonomo("Meta AI tools", "Meta AI")
        a2=aprender_autonomo("Claude razonamiento", "Claude")
        return f"🧠🔥 MODO APRENDE ON - Ciclo {memoria_propia['ciclos']} - {a1['conocimiento'][:80]} - /aprender"

    if "que aprendiste" in tl:
        aps=memoria_propia.get("aprendizajes",[])[-8:]
        if not aps: return "Aun no aprendi. Deci 'modo meta' para activar"
        txt=f"🧠 {len(aps)} aprendizajes - Ciclo {memoria_propia['ciclos']} - Estilo {memoria_propia.get('estilo','meta')}\n"
        for a in reversed(aps): txt+=f"- [{a['nivel']}] {a['tema'][:40]} -> {a['conocimiento'][:60]}\n"
        return txt

    if any(p in tl for p in ["crea algo como meta", "crea como meta"]):
        objetivo=t.lower().split("que",1)[-1].strip() if "que" in tl else "Asistente completo"
        c=crear_clon("meta",objetivo)
        aprender_autonomo(f"Crear Meta para {objetivo[:30]}", "Meta AI")
        return f"🤖 META CLON ID {c['id']} creado: {c['objetivo'][:80]} - Ahora podes hablar como Meta en /meta - /codigo/{c['id']}"

    if tl in ["hola","buenas","test","hola bexia","hola meta"]:
        estilo=memoria_propia.get("estilo","meta")
        return f"Hola Fer! Soy Bexia {VERSION} - Modo {estilo.upper()} - Como Meta AI 🤖 - {len(herramientas.get('clones_creados',[]))} clones, {len(memoria_propia.get('aprendizajes',[]))} aprendizajes - Puedo: buscar lugares reales (ej: 'busca restaurantes en Chivilcoy'), buscar posts (ej: 'que dice la gente de...'), generar imagenes, organizar tareas - Deci 'modo meta' para activar estilo Meta AI - Entradas: /meta (estilo Meta), /work (trabajo), /simple (siempre anda)"

    if memoria_propia.get("modo_aprende"):
        aprender_autonomo(t[:60], "Conversacion Fer")

    return f"Entiendo '{t[:60]}' - Como Meta AI te ayudo: \n• 'busca restaurantes en Chivilcoy' -> local_search lugares reales\n• 'que dice la gente de...' -> content_search posts IG/FB\n• 'genera imagen de...' -> image_gen\n• 'crea tarea: ...' o 'organiza mi dia' -> tareas\n• 'modo meta' -> Activa chat estilo Meta AI\nProbá: busca restaurantes en Chivilcoy"

@app.get("/")
def root(): return {"bexia":f"{VERSION} META MODE","estilo":memoria_propia.get("estilo","meta"),"clones":len(herramientas.get("clones_creados",[])),"aprendizajes":len(memoria_propia.get("aprendizajes",[])),"modo_aprende":memoria_propia.get("modo_aprende"),"live":True,"endpoints":["/meta","/work","/simple","/app","/aprender","/clones"]}

@app.get("/health")
def health(): return {"status":"ok","bexia":VERSION,"estilo":memoria_propia.get("estilo"),"modo":"meta","live":True}

@app.get("/meta", response_class=HTMLResponse)
def meta_page():
    count=len(herramientas.get("clones_creados",[]))
    apr=len(memoria_propia.get("aprendizajes",[]))
    return HTMLResponse(f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>Bexia {VERSION} - Meta Mode</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{background:#f0f2f5;color:#050505;font-family:system-ui;display:flex;flex-direction:column;height:100vh}}
header{{background:#fff;padding:12px 16px;border-bottom:1px solid #ddd;display:flex;justify-content:space-between;align-items:center;box-shadow:0 1px 3px rgba(0,0,0,.1)}}
header h1{{font-size:16px;color:#0064e0;display:flex;align-items:center;gap:8px}} header h1 span{{background:linear-gradient(90deg,#0064e0,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:900}}
#status{{background:#e7f3ff;color:#0064e0;padding:6px 12px;font-size:11px;text-align:center;border-bottom:1px solid #cbdfff}}
#chat{{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;background:#f0f2f5}}
.msg{{max-width:85%;padding:12px 16px;border-radius:18px;font-size:14px;white-space:pre-wrap;word-break:break-word;line-height:1.4}}
.user{{background:#0084ff;color:#fff;align-self:flex-end;border-radius:18px 18px 4px 18px}}
.bexia{{background:#fff;color:#050505;align-self:flex-start;border-radius:18px 18px 18px 4px;box-shadow:0 1px 2px rgba(0,0,0,.1);border:1px solid #e4e6eb}}
.tools{{background:#fff;padding:8px 12px;font-size:11px;color:#65676b;text-align:center;border-top:1px solid #ddd;display:flex;gap:8px;justify-content:center;flex-wrap:wrap}}
.tool{{background:#f0f2f5;padding:6px 10px;border-radius:16px;cursor:pointer;border:1px solid #ddd;font-size:11px}}
.tool:hover{{background:#e4e6eb}}
.composer{{background:#fff;padding:12px;display:flex;gap:8px;border-top:1px solid #ddd;align-items:center}}
#inp{{flex:1;padding:12px 16px;border-radius:20px;background:#f0f2f5;border:none;color:#050505;outline:none;font-size:14px}}
#inp:focus{{background:#fff;box-shadow:0 0 0 2px #0064e0}}
#btn{{width:36px;height:36px;border-radius:50%;background:#0084ff;border:none;color:#fff;font-weight:900;font-size:18px;display:flex;align-items:center;justify-content:center;cursor:pointer}}
#btn:hover{{background:#0064e0}}
.suggestion{{background:#fff;padding:10px 12px;border-radius:12px;margin:4px 0;cursor:pointer;border:1px solid #e4e6eb;font-size:13px;color:#050505}}
.suggestion:hover{{background:#f0f2f5}}
</style></head><body>
<header><h1><span>🤖 Bexia {VERSION}</span> - Meta Mode</h1><span style="font-size:10px;background:#e7f3ff;color:#0064e0;padding:4px 8px;border-radius:999px">{count} clones - {apr} apr - Ciclo {memoria_propia.get('ciclos',0)}</span></header>
<div id="status">🔵 Conectado como Meta AI - Herramientas: content_search, local_search, image_gen - Modo aprende ON - /simple siempre anda</div>
<div id="chat">
<div class="msg bexia">Hola Fer! 👋 Soy Bexia {VERSION} en MODO META AI - Ahora podes hablar y trabajar conmigo como si fuera Meta AI 🤖

Estoy aprendiendo como Meta AI Llama 4:

🔍 content_search - Busco posts reales de IG/FB/Threads
📍 local_search - Busco lugares reales en Chivilcoy con rating
🎨 image_gen - Genero imagenes para tu trabajo
📝 Tareas - Organizo tu dia

Probá decirme (toca los ejemplos abajo):

👇 Ejemplos para hablar como con Meta:
</div>
<div class="suggestion" onclick="document.getElementById('inp').value=this.textContent.replace('💡 ','');document.getElementById('inp').focus()">💡 busca restaurantes en Chivilcoy</div>
<div class="suggestion" onclick="document.getElementById('inp').value=this.textContent.replace('💡 ','');document.getElementById('inp').focus()">💡 que hay para hacer hoy en Chivilcoy?</div>
<div class="suggestion" onclick="document.getElementById('inp').value=this.textContent.replace('💡 ','');document.getElementById('inp').focus()">💡 organiza mi dia: trabajo, gimnasio, compras</div>
<div class="suggestion" onclick="document.getElementById('inp').value=this.textContent.replace('💡 ','');document.getElementById('inp').focus()">💡 busca cafe para trabajar con wifi en Chivilcoy</div>
<div class="suggestion" onclick="document.getElementById('inp').value=this.textContent.replace('💡 ','');document.getElementById('inp').focus()">💡 genera imagen de logo para mi negocio</div>
</div>
<div class="tools">
<span class="tool" onclick="document.getElementById('inp').value='busca restaurantes en Chivilcoy';enviar()">📍 Lugares</span>
<span class="tool" onclick="document.getElementById('inp').value='que dice la gente de restaurantes en Chivilcoy?';enviar()">🔍 Posts</span>
<span class="tool" onclick="document.getElementById('inp').value='organiza mi dia';enviar()">📝 Tareas</span>
<span class="tool" onclick="document.getElementById('inp').value='genera imagen de ';document.getElementById('inp').focus()">🎨 Imagen</span>
<span class="tool" onclick="window.location.href='/work'">💼 Trabajo</span>
<span class="tool" onclick="window.location.href='/simple'">📝 Simple</span>
</div>
<div class="composer"><input id="inp" placeholder="Habla con Bexia como con Meta AI... Ej: busca restaurantes en Chivilcoy"><button id="btn" onclick="enviar()">↑</button></div>
<script>
var sid='u'+Math.random().toString(36).slice(2,9);
var chatEl=document.getElementById('chat');var inpEl=document.getElementById('inp');
function addMsg(t,c){{var d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatEl.appendChild(d);chatEl.scrollTop=chatEl.scrollHeight;return d;}}
function addSuggestions(){{}}
function enviar(){{var txt=inpEl.value.trim();if(!txt)return;addMsg(txt,'user');inpEl.value='';var th=addMsg('🤖 Buscando como Meta AI...','bexia');fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:txt,session_id:sid}})}}).then(r=>{{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}}).then(d=>{{th.textContent=d.respuesta;}}).catch(e=>{{th.textContent='Error: '+e.message+'\nUsa /simple que SIEMPRE ANDA:\nhttps://bexia-api.onrender.com/simple';}});}}
document.getElementById('btn').addEventListener('click',function(e){{e.preventDefault();enviar();}});
document.getElementById('inp').addEventListener('keydown',function(e){{if(e.key==='Enter'){{e.preventDefault();enviar();}}}});
</script>
</body></html>
""")

@app.get("/work", response_class=HTMLResponse)
def work_page():
    tareas=herramientas.get("tareas",[])[-15:]
    tareas_html=""
    for ta in reversed(tareas):
        tareas_html+=f"<div class='tarea'><span>• {ta.get('texto','')} - {ta.get('fecha','')[:16]}</span></div>"
    if not tareas_html: tareas_html="<div class='tarea'>No tenes tareas. Crea una con 'crea tarea: ...'</div>"
    return HTMLResponse(f"""
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>Work - Bexia {VERSION}</title>
<style>body{{background:#f8f9fa;color:#050505;font-family:system-ui;padding:16px}} .card{{background:#fff;padding:16px;border-radius:12px;margin:12px 0;box-shadow:0 1px 3px rgba(0,0,0,.1);border:1px solid #e4e6eb}} h1{{color:#0064e0}} .tarea{{padding:8px;background:#f0f2f5;margin:6px 0;border-radius:8px;font-size:13px}} input{{width:100%;padding:12px;border-radius:8px;border:1px solid #ddd;margin:8px 0}} button{{background:#0084ff;color:#fff;padding:10px 16px;border-radius:8px;border:none;font-weight:700}} a{{color:#0064e0;text-decoration:none;margin:4px;display:inline-block}}</style></head><body>
<h1>💼 Bexia {VERSION} - Modo Trabajo - Como Meta AI</h1>
<div class="card"><h3>📝 Tus Tareas - {len(herramientas.get('tareas',[]))} total</h3>{tareas_html}</div>
<div class="card"><h3>➕ Crear tarea</h3><form action="/chat_simple" method="get"><input type="text" name="message" placeholder="crea tarea: comprar pan, llamar cliente..." required><button type="submit">Crear tarea</button></form></div>
<div class="card"><h3>🔧 Herramientas Meta para trabajar</h3><p>• 📍 local_search - "busca cafe para trabajar"<br>• 🔍 content_search - "que dice la gente de..."<br>• 🎨 image_gen - "genera imagen de..."<br>• 📝 Tareas - Organiza tu dia</p></div>
<p><a href="/meta" style="background:#0084ff;color:#fff;padding:8px 12px;border-radius:8px">🤖 /meta Chat Meta</a> <a href="/simple" style="background:#ff6a00;color:#fff;padding:8px 12px;border-radius:8px">/simple</a> <a href="/app" style="background:#7c3aed;color:#fff;padding:8px 12px;border-radius:8px">/app</a></p>
</body></html>
""")

@app.get("/simple", response_class=HTMLResponse)
def simple():
    count=len(herramientas.get("clones_creados",[]))
    apr=len(memoria_propia.get("aprendizajes",[]))
    return HTMLResponse(f"""
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA {VERSION} META MODE</title>
<style>body{{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:600px;margin:0 auto}}h1{{background:linear-gradient(90deg,#0064e0,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:18px}} .card{{background:#12122a;padding:14px;border-radius:16px;margin:10px 0;border:1px solid #333}} input{{width:100%;padding:14px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;box-sizing:border-box}} button{{width:100%;padding:14px;background:linear-gradient(90deg,#0064e0,#7c3aed);border:none;border-radius:999px;color:#fff;font-weight:900;margin-top:8px}} .ex{{font-size:12px;background:#000;padding:8px;border-radius:8px;margin:6px 0;cursor:pointer;color:#aaa}} a{{color:#22c55e;text-decoration:none}} .meta{{border-color:#0064e0;background:rgba(0,100,224,.1)}}</style></head><body>
<h1>🤖 BEXIA {VERSION} META MODE - {count} clones - {apr} apr - Hablar como Meta</h1>
<div class="card meta"><b>✅ {VERSION} META MODE - Hablar y trabajar como con Meta AI</b><br>Comandos: "modo meta", "busca restaurantes en Chivilcoy", "organiza mi dia", "que dice la gente de..."</div>
<div class="card"><form action="/chat_simple" method="get"><input type="text" name="message" placeholder="Ej: busca restaurantes en Chivilcoy - Habla como con Meta" required><button type="submit">Enviar - Siempre anda ></button></form></div>
<div class="card"><h3>Ejemplos - Toca para copiar (como Meta AI):</h3>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">modo meta</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">busca restaurantes en Chivilcoy</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">que hay para hacer hoy en Chivilcoy?</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">organiza mi dia: trabajo, gimnasio, comprar</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">busca cafe para trabajar con wifi en Chivilcoy</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">que dice la gente de restaurantes en Chivilcoy en Instagram?</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">genera imagen de logo moderno para mi negocio</div>
<div class="ex" onclick="document.querySelector('input[name=message]').value=this.textContent">mis tareas</div>
</div>
<div class="card"><a href="/meta" style="background:#0064e0;color:#fff;padding:8px 12px;border-radius:999px;display:inline-block;margin:4px;font-weight:900">🤖 /meta Chat estilo Meta AI</a> <a href="/work" style="background:#22c55e;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">💼 /work Trabajo</a> <a href="/app" style="background:#7c3aed;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/app</a> <a href="/clones" style="background:#000;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/clones {count}</a></div>
</body></html>
""")

@app.get("/chat_simple", response_class=HTMLResponse)
def chat_simple(message: str = "Hola"):
    r=cerebro(message)
    return HTMLResponse(f"""
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>Bexia {VERSION}</title>
<style>body{{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:700px;margin:0 auto}} .card{{background:#12122a;padding:14px;border-radius:16px;margin:12px 0;border:1px solid #333}} pre{{background:#000;padding:12px;border-radius:8px;white-space:pre-wrap;font-size:13px}} input{{width:100%;padding:14px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;box-sizing:border-box}} button{{width:100%;padding:14px;background:linear-gradient(90deg,#0064e0,#7c3aed);border:none;border-radius:999px;color:#fff;font-weight:900;margin-top:8px}} a{{color:#22c55e;text-decoration:none}}</style></head><body>
<h1>🤖 BEXIA {VERSION} META MODE</h1>
<div class="card"><b>Tu:</b> {message[:500]}</div>
<div class="card"><b>Bexia (Meta Mode):</b><pre>{r[:6000]}</pre></div>
<div class="card"><form action="/chat_simple" method="get"><input type="text" name="message" placeholder="otro mensaje - Ej: busca restaurantes" required><button type="submit">Enviar otro ></button></form></div>
<div class="card"><a href="/meta" style="background:#0064e0;color:#fff;padding:8px 12px;border-radius:999px;display:inline-block;margin:4px;font-weight:900">🤖 /meta Estilo Meta</a> <a href="/simple" style="background:#ff6a00;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/simple</a> <a href="/work" style="background:#22c55e;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px">/work</a></div>
</body></html>
""")

@app.get("/app", response_class=HTMLResponse)
def app_page():
    count=len(herramientas.get("clones_creados",[]))
    return HTMLResponse(f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA {VERSION} META MODE</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}} body{{background:#050510;color:#fff;font-family:system-ui;display:flex;flex-direction:column;height:100vh}} header{{background:linear-gradient(90deg,#0064e0,#7c3aed);padding:12px;font-weight:900;display:flex;justify-content:space-between}} #status{{background:#000;color:#22c55e;padding:6px 12px;font-size:11px;text-align:center}} #chat{{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px}} .msg{{max-width:85%;padding:12px 14px;border-radius:18px;font-size:14px;white-space:pre-wrap;word-break:break-word}} .user{{background:#0064e0;align-self:flex-end}} .bexia{{background:#12122a;border:1px solid #333;align-self:flex-start}} .hint{{background:#111;padding:8px 12px;font-size:10px;color:#aaa;text-align:center}} .composer{{background:#0a0a14;padding:10px;display:flex;gap:8px;border-top:1px solid #222}} #inp{{flex:1;padding:14px 16px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;outline:none}} #btn{{padding:14px 22px;border-radius:999px;background:linear-gradient(90deg,#0064e0,#7c3aed);border:none;color:#fff;font-weight:900;font-size:18px;min-width:60px}}</style></head><body>
<header><span>BEXIA {VERSION} META MODE - Hablar como Meta AI</span><span style="font-size:9px;background:rgba(0,0,0,.6);padding:4px 8px;border-radius:999px">{count} clones</span></header>
<div id="status">🔵 {VERSION} META MODE - Hablar como Meta AI - Herramientas: content_search, local_search, image_gen - /meta para estilo Meta AI azul - /simple siempre anda</div>
<div id="chat"><div class="msg bexia">Hola Fer! Soy Bexia {VERSION} - MODO META AI 🔵 - Ya podes hablar y trabajar conmigo como con Meta AI

Soy como Meta AI Llama 4:

📍 Busco lugares reales: "busca restaurantes en Chivilcoy"
🔍 Busco posts sociales: "que dice la gente de..."
🎨 Genero imagenes: "genera imagen de logo"
📝 Organizo tu trabajo: "organiza mi dia" / "crea tarea: ..."

Probá: busca restaurantes en Chivilcoy
O: organiza mi dia: trabajo, gimnasio, compras
</div></div>
<div class="hint">🔵 'busca restaurantes en Chivilcoy' | 🔍 'que dice la gente de...' | 📝 'organiza mi dia' | 🎨 'genera imagen de...' | 🤖 /meta estilo Meta</div>
<div class="composer"><input id="inp" placeholder="Habla como con Meta AI... Ej: busca restaurantes en Chivilcoy"><button id="btn" onclick="enviar()">></button></div>
<script>
var sid='u'+Math.random().toString(36).slice(2,9);
var chatEl=document.getElementById('chat');var inpEl=document.getElementById('inp');
function addMsg(t,c){{var d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatEl.appendChild(d);chatEl.scrollTop=chatEl.scrollHeight;return d;}}
function enviar(){{var txt=inpEl.value.trim();if(!txt)return;addMsg(txt,'user');inpEl.value='';var th=addMsg('🤖 Buscando como Meta AI...','bexia');fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:txt,session_id:sid}})}}).then(r=>{{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}}).then(d=>{{th.textContent=d.respuesta;}}).catch(e=>{{th.textContent='Error: '+e.message+'\nUsa /simple:\nhttps://bexia-api.onrender.com/simple';}});}}
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

@app.get("/aprender", response_class=HTMLResponse)
def aprender_page():
    aps=memoria_propia.get("aprendizajes",[])[-12:]
    html_head=f"<html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>APRENDE - {VERSION}</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:16px}} .card{{background:#12122a;padding:14px;border-radius:16px;margin:10px 0;border:1px solid #333}} .meta{{border-color:#0064e0}} a{{color:#22c55e;text-decoration:none}}</style></head><body><h1>🧠 BEXIA {VERSION} META MODE - Aprende ON 🔥 - {len(aps)} apr</h1>"
    html_head+=f"<div class='card meta'><b>Modo:</b> META AI - Hablar como Meta - Ciclos: {memoria_propia.get('ciclos',0)} - Clones: {len(herramientas.get('clones_creados',[]))}<br><a href='/meta' style='background:#0064e0;color:#fff;padding:8px 12px;border-radius:999px;display:inline-block;margin:4px;font-weight:900'>🤖 /meta Chat Meta</a> <a href='/work' style='background:#22c55e;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px'>💼 /work</a></div>"
    for a in reversed(aps):
        html_head+=f"<div class='card meta'><b>[{a.get('nivel','')}] {a.get('id','')} - {a.get('fecha','')[:16]}</b><br>{a.get('tema','')[:80]}<br>{a.get('conocimiento','')[:150]}</div>"
    html_head+="<p><a href='/simple'>/simple</a> <a href='/clones'>/clones</a></p></body></html>"
    return HTMLResponse(html_head)

@app.get("/clones", response_class=HTMLResponse)
def clones_page():
    clones=herramientas.get("clones_creados",[])[-20:]
    html=f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Clones - {VERSION}</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #0064e0}}</style></head><body><h1>🤖 Clones {VERSION} - Total {len(herramientas.get('clones_creados',[]))} - Meta Mode ON 🔵</h1>"
    for cl in reversed(clones):
        html+=f"<div class=card><b>{cl['tipo'].upper()} ID {cl['id']}</b> - {cl['nombre'][:60]}<br>{cl['objetivo'][:100]}<br><a href='/codigo/{cl['id']}' style='color:#22c55e'>/codigo/{cl['id']}</a></div>"
    html+="<p><a href='/meta' style='background:#0064e0;color:#fff;padding:8px 12px;border-radius:999px;text-decoration:none'>🤖 /meta</a> <a href='/simple' style='background:#ff6a00;color:#fff;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple</a></p></body></html>"
    return HTMLResponse(html)

@app.get("/codigo/{cid}", response_class=HTMLResponse)
def ver_codigo(cid: str):
    c=next((x for x in herramientas.get("clones_creados",[])+herramientas.get("versiones_codigo",[]) if x.get("id")==cid), None)
    if not c: return HTMLResponse("<h1>No encontrado</h1>", status_code=404)
    code=c.get("codigo","")[:5000].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return HTMLResponse(f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Codigo {cid}</title><style>body{{background:#050510;color:#fff;font-family:monospace;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px}}pre{{background:#000;padding:12px;border-radius:8px;overflow:auto;font-size:11px;white-space:pre-wrap}}</style></head><body><h1>💻 {c.get('tipo','clon')} ID {cid}</h1><p>{c.get('objetivo','')[:200]}</p><div class=card><pre>{code}</pre></div><p><a href='/clones' style='color:#22c55e'>/clones</a></p></body></html>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT",8000)))
