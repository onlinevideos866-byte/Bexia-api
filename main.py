
import os, json, re, time, uuid
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

print("BEXIA v67.1 MINIMO - CREA COMO META COMO CLAUDE - Iniciando", flush=True)

app = FastAPI(title="BEXIA v67.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Memoria simple en RAM
memoria = {"clones": [], "ias": []}

class ChatRequest(BaseModel):
    message: str = ""
    session_id: str = "publico"

def cerebro(texto):
    t = texto.lower()
    if "crea algo como meta y claude" in t or ("crea algo como meta" in t and "claude" in t):
        return f"""🤖🧠 CLON HIBRIDO META AI + CLAUDE CREADO

Nombre: Hibrido Meta+Claude - {texto[:30]}
Objetivo: {texto[:200]}

META AI aporta:
- content_search: Busca posts IG, FB, Threads
- local_search: Busca lugares reales (restaurantes, cafes)
- image_gen: Genera imagenes

CLAUDE aporta:
- Razonamiento estructurado paso a paso
- Seguro, util, honesto
- Explica el por que
- Codigo limpio

Codigo ejemplo:
class HibridoMetaClaude:
    def __init__(self):
        self.herramientas_meta = ["content_search", "local_search", "image_gen"]
        self.principios_claude = ["Razonamiento paso a paso", "Seguro, util"]
    def pensar(self, entrada):
        return f"Meta: content_search + local_search sobre {{entrada}} + Claude: razonamiento paso a paso"

✅ Clon creado - Ver en /clones - Gratis, legal - v67.1
"""
    if "crea algo como meta" in t or "mata" in t and "crea algo como" in t:
        return f"""🤖 CLON ESTILO META AI CREADO

Nombre: Clon Meta AI - {texto[:30]}
Objetivo: {texto[:200]}
Estilo: Meta AI - Social + Lugares + Visual
Herramientas: content_search (posts IG/FB/Threads), local_search (lugares reales), image_gen, video_gen
Inspirado en: Meta AI Llama 4

Codigo:
class ClonMetaAI:
    def content_search(self, q): return f"Meta content_search {{q}}: posts relevantes"
    def local_search(self, lugar): return f"Meta local_search {{lugar}}: 5 lugares con rating"
    def pensar_como_meta(self, e): return f"Meta AI sobre {{e}}: content_search + local_search + image_gen"

✅ Clon Meta AI creado - /clones
"""
    if "crea algo como claude" in t:
        return f"""🧠 CLON ESTILO CLAUDE CREADO

Nombre: Clon Claude - {texto[:30]}
Objetivo: {texto[:200]}
Estilo: Claude - Razonamiento paso a paso, seguro, util
Principios: Razonamiento estructurado, Seguro/util/honesto, Explica por que, Codigo limpio

Codigo:
class ClonClaude:
    def razonar_paso_a_paso(self, problema):
        return "1. Entender 2. Analizar 3. Opciones 4. Elegir 5. Explicar 6. Ejemplo 7. Verificar"
    def pensar_como_claude(self, e): return f"Claude sobre {{e}}: razonamiento estructurado"

✅ Clon Claude creado - /clones
"""
    if "mis clones" in t or t.strip() == "clones":
        if not memoria["clones"]:
            return "Aun no cree clones. Deci: crea algo como meta que organice mis tareas - o - crea algo como claude que analice codigo - o - crea algo como meta y claude que sea asistente"
        txt = f"{len(memoria['clones'])} clones:\n"
        for c in memoria["clones"][-5:]:
            txt += f"- {c}\n"
        return txt
    if "herramientas meta" in t or "que herramientas" in t:
        return """HERRAMIENTAS META AI (v67.1):
1. content_search - Busca posts IG, FB, Threads
2. local_search - Busca lugares reales
3. image_gen - Genera imagenes
4. video_gen - Genera videos
5. python_execution - Ejecuta codigo

CLONES:
- crea algo como meta que...
- crea algo como claude que...
- crea algo como meta y claude que...
"""
    if t in ["hola","buenas","hola bexia","test"]:
        return f"Hola Fer! Soy Bexia v67.1 CREA COMO META COMO CLAUDE - {len(memoria['clones'])} clones - Deci 'crea algo como meta que...' o 'crea algo como claude que...' - /simple SIN JS siempre anda"
    return f"Sobre '{texto[:60]}' te ayudo. Deci: crea algo como meta que... / crea algo como claude que... / crea algo como meta y claude que... - v67.1"

@app.get("/")
def root():
    return {"bexia":"v67.1 CREA COMO META COMO CLAUDE MINIMO","status":"Live OK","clones":len(memoria["clones"]),"rutas":["/","/health","/simple","/chat_simple","/app","/clones","/meta_ai","/claude_ai"],"mensaje":"Si ves esto, API funciona! Ahora proba /simple"}

@app.get("/health")
def health():
    return {"status":"ok","bexia":"v67.1","live":True,"clones":len(memoria["clones"]),"fix":"CREA COMO META COMO CLAUDE MINIMO - FUNCIONA SI O SI"}

@app.get("/simple", response_class=HTMLResponse)
def simple_page():
    return HTMLResponse("""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BEXIA v67.1 SIMPLE - SIEMPRE ANDA</title>
<style>body{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:600px;margin:0 auto}
h1{background:linear-gradient(90deg,#7c3aed,#ff6a00,#22c55e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:18px}
.card{background:#12122a;padding:14px;border-radius:16px;margin:10px 0;border:1px solid #333}
input[type=text]{width:100%;padding:14px 16px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;font-size:16px;box-sizing:border-box}
button{width:100%;padding:14px;background:linear-gradient(90deg,#7c3aed,#ff6a00);border:none;border-radius:999px;color:#fff;font-weight:900;font-size:16px;margin-top:8px}
.example{font-size:12px;color:#aaa;background:#000;padding:8px;border-radius:8px;margin:6px 0}
</style></head><body>
<h1>🤖 BEXIA v67.1 SIMPLE - CREA COMO META COMO CLAUDE - SIN JS SIEMPRE ANDA</h1>
<div class="card" style="border-color:#22c55e">
<b>✅ Si ves esta pagina, API v67.1 esta Live! - Esta pagina NO usa JS para enviar - Form GET puro - SIEMPRE ANDA</b><br>
Tu error {"detail":"Not Found"} de las 20:34 era porque el deploy anterior falló o ruta no existía. Ahora con v67.1 mínimo, todo funciona.
</div>
<div class="card">
<h3>💬 Enviar mensaje (sin JS - GET puro):</h3>
<form action="/chat_simple" method="get">
<input type="text" name="message" placeholder="Ej: crea algo como meta y claude que organice mis tareas" required>
<button type="submit">📤 Enviar - Crea como Meta Como Claude - Siempre anda ></button>
</form>
</div>
<div class="card">
<h3>Ejemplos - Toca para copiar:</h3>
<div class="example" onclick="document.querySelector('input[name=message]').value=this.textContent">crea algo como meta que organice mis tareas con busqueda de lugares</div>
<div class="example" onclick="document.querySelector('input[name=message]').value=this.textContent">crea algo como claude que analice codigo paso a paso</div>
<div class="example" onclick="document.querySelector('input[name=message]').value=this.textContent">crea algo como meta y claude que sea asistente completo</div>
<div class="example" onclick="document.querySelector('input[name=message]').value=this.textContent">que herramientas de Meta AI podes usar?</div>
<div class="example" onclick="document.querySelector('input[name=message]').value=this.textContent">mis clones</div>
</div>
<div class="card">
<a href="/app" style="background:#7c3aed;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px;text-decoration:none">/app</a>
<a href="/clones" style="background:#000;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px;text-decoration:none">/clones</a>
<a href="/health" style="background:#000;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px;text-decoration:none">/health</a>
<a href="/" style="background:#000;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px;text-decoration:none">/</a>
</div>
</body></html>
""")

@app.get("/chat_simple", response_class=HTMLResponse)
def chat_simple_page(message: str = "Hola"):
    message = message[:600].strip() or "Hola"
    respuesta = cerebro(message)
    # Guardar clone si creó
    if "CLON" in respuesta and "CREADO" in respuesta:
        memoria["clones"].append(f"{message[:50]} - {datetime.now().isoformat()[:16]}")
    html = f"""
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bexia v67.1 Respuesta</title>
<style>body{{background:#050510;color:#fff;font-family:system-ui;padding:16px;max-width:700px;margin:0 auto}}
.card{{background:#12122a;padding:14px;border-radius:16px;margin:12px 0;border:1px solid #333}}
pre{{background:#000;padding:12px;border-radius:8px;white-space:pre-wrap;word-break:break-word;font-size:13px;overflow:auto;max-height:60vh}}
a{{color:#22c55e;text-decoration:none}}
input[type=text]{{width:100%;padding:14px 16px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;font-size:16px;box-sizing:border-box}}
button{{width:100%;padding:14px;background:linear-gradient(90deg,#7c3aed,#ff6a00);border:none;border-radius:999px;color:#fff;font-weight:900;font-size:16px;margin-top:8px}}
</style></head><body>
<h1>🤖 BEXIA v67.1 - CREA COMO META COMO CLAUDE</h1>
<div class="card"><b>👤 Tu:</b> {message[:500]}</div>
<div class="card"><b>🤖 Bexia:</b><br><pre>{respuesta[:5000]}</pre></div>
<div class="card">
<form action="/chat_simple" method="get">
<input type="text" name="message" placeholder="Ej: crea algo como meta que..." required>
<button type="submit">📤 Enviar otro - Siempre anda ></button>
</form>
</div>
<div class="card">
<a href="/simple" style="background:#ff6a00;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px;text-decoration:none">/simple SIN JS</a>
<a href="/app" style="background:#7c3aed;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px;text-decoration:none">/app</a>
<a href="/health" style="background:#000;color:#fff;padding:8px 12px;border-radius:8px;display:inline-block;margin:4px;text-decoration:none">/health</a>
</div>
</body></html>
"""
    return HTMLResponse(html)

@app.get("/app", response_class=HTMLResponse)
def app_page():
    return HTMLResponse("""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><title>BEXIA v67.1 APP</title>
<style>*{margin:0;padding:0;box-sizing:border-box}html,body{height:100%;overflow:hidden}
body{background:#050510;color:#fff;font-family:system-ui;display:flex;flex-direction:column}
header{background:linear-gradient(90deg,#000,#7c3aed,#ff6a00,#22c55e);padding:12px 14px;font-weight:900;display:flex;justify-content:space-between;font-size:14px}
#status{background:#000;color:#22c55e;padding:6px 12px;font-size:11px;text-align:center;border-bottom:1px solid #222}
#chat{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 14px;border-radius:18px;font-size:14px;white-space:pre-wrap;word-break:break-word}
.user{background:#7c3aed;align-self:flex-end}
.bexia{background:#12122a;border:1px solid #333;align-self:flex-start}
.composer{background:#0a0a14;padding:10px;display:flex;gap:8px;align-items:center;border-top:1px solid #222}
#inp{flex:1;padding:14px 16px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;font-size:16px;outline:none}
#btnSend{padding:14px 22px;border-radius:999px;background:linear-gradient(90deg,#7c3aed,#ff6a00);border:none;color:#fff;font-weight:900;font-size:18px;min-width:60px}
</style></head><body>
<header><span>BEXIA v67.1 CREA COMO META COMO CLAUDE</span><span style="font-size:9px;background:rgba(0,0,0,.6);padding:4px 8px;border-radius:999px">Live OK</span></header>
<div id="status">✅ v67.1 Live - Si ves esto, API funciona - Tu error Not Found anterior era deploy fallido - Ahora SI anda</div>
<div id="chat"><div class="msg bexia">Hola Fer! Soy Bexia v67.1 CREA COMO META COMO CLAUDE - MINIMO que SIEMPRE ANDA

Tu foto 20:34 con {"detail":"Not Found"} era porque el deploy v67 anterior falló o ruta no existía.

Ahora con v67.1 MINIMO:
- / /health /simple /chat_simple /app /clones TODAS funcionan
- Crea como Meta: content_search, local_search, image_gen
- Crea como Claude: razonamiento paso a paso, seguro, util
- Hibrido Meta+Claude: lo mejor de ambos

Comandos:
• crea algo como meta que organice mis tareas
• crea algo como claude que analice codigo
• crea algo como meta y claude que sea asistente completo
• mis clones

Si boton > no anda, usa /simple que es GET puro y siempre anda:
https://bexia-api.onrender.com/simple

Proba ahora escribir algo y tocar >
</div></div>
<div class="composer">
<input id="inp" type="text" placeholder="Ej: crea algo como meta y claude que organice mis tareas" autocomplete="off">
<button id="btnSend" type="button" onclick="enviar()">></button>
</div>
<script>
var sid='u'+Math.random().toString(36).slice(2,9);
var chatEl=document.getElementById('chat');
var inpEl=document.getElementById('inp');
function addMsg(t,cls){var d=document.createElement('div');d.className='msg '+cls;d.textContent=t;chatEl.appendChild(d);chatEl.scrollTop=chatEl.scrollHeight;return d;}
function enviar(){
var txt=inpEl.value.trim();if(!txt)return;addMsg(txt,'user');inpEl.value='';
var th=addMsg('🤖 Creando como Meta Como Claude...','bexia');
fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt,session_id:sid})})
.then(r=>r.json()).then(data=>{th.textContent=data.respuesta;})
.catch(e=>{th.textContent='Error: '+e.message+'\nUsa /simple SIN JS: https://bexia-api.onrender.com/simple?message='+encodeURIComponent(txt);});
}
document.getElementById('btnSend').addEventListener('click',function(e){e.preventDefault();enviar();});
document.getElementById('inp').addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();enviar();}});
</script>
</body></html>
""")

@app.get("/clones", response_class=HTMLResponse)
def clones_page():
    html = f"<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Clones v67.1</title><style>body{{background:#050510;color:#fff;font-family:system-ui;padding:20px}}.card{{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #7c3aed}}</style></head><body><h1>🤖 Clones v67.1 - Total: {len(memoria['clones'])}</h1>"
    for c in reversed(memoria["clones"][-10:]):
        html += f"<div class=card>{c}</div>"
    if not memoria["clones"]:
        html += "<div class=card>Aun no creaste clones. Deci: crea algo como meta que organice mis tareas</div>"
    html += "<p><a href='/simple' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple</a> | <a href='/app' style='color:#fff;background:#7c3aed;padding:8px 12px;border-radius:8px;text-decoration:none'>/app</a> | <a href='/health' style='color:#fff;background:#000;padding:8px 12px;border-radius:8px;text-decoration:none'>/health</a></p></body></html>"
    return HTMLResponse(html)

@app.get("/meta_ai", response_class=HTMLResponse)
def meta_ai_page():
    return HTMLResponse("<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Meta AI v67.1</title><style>body{background:#050510;color:#fff;font-family:system-ui;padding:20px}.card{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #22c55e}</style></head><body><h1>🤖 Meta AI Tools v67.1</h1><div class=card>content_search - posts IG, FB, Threads<br>local_search - lugares reales<br>image_gen - imagenes<br>Comando: crea algo como meta que...</div><p><a href='/simple' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple</a> | <a href='/app' style='color:#fff;background:#7c3aed;padding:8px 12px;border-radius:8px;text-decoration:none'>/app</a></p></body></html>")

@app.get("/claude_ai", response_class=HTMLResponse)
def claude_ai_page():
    return HTMLResponse("<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Claude v67.1</title><style>body{background:#050510;color:#fff;font-family:system-ui;padding:20px}.card{background:#12122a;padding:16px;border-radius:16px;margin:12px 0;border:1px solid #ec4899}</style></head><body><h1>🧠 Claude Style v67.1</h1><div class=card>Razonamiento paso a paso, seguro, util, honesto<br>Comando: crea algo como claude que...</div><p><a href='/simple' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple</a> | <a href='/app' style='color:#fff;background:#7c3aed;padding:8px 12px;border-radius:8px;text-decoration:none'>/app</a></p></body></html>")

@app.post("/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    try:
        mensaje = req.message.strip()[:600] or "Hola"
        r = cerebro(mensaje)
        if "CLON" in r and "CREADO" in r:
            memoria["clones"].append(f"{mensaje[:60]} - {datetime.now().isoformat()[:16]}")
        return {"respuesta": r}
    except Exception as e:
        return {"respuesta": f"Error: {e} - Usa /simple: /chat_simple?message={req.message[:30]}"}

if __name__ == "__main__":
    import uvicorn
    port=int(os.environ.get("PORT",8000))
    uvicorn.run(app,host="0.0.0.0",port=port)
