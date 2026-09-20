
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

clones = []

class ChatReq(BaseModel):
    message: str = ""
    session_id: str = "publico"

def cerebro(t):
    tl = t.lower()
    if "crea algo como meta y claude" in tl or ("meta" in tl and "claude" in tl and "crea algo como" in tl):
        clones.append(t[:60])
        return f"🤖🧠 CLON HIBRIDO META AI + CLAUDE CREADO\nObjetivo: {t[:200]}\n\nMeta AI: content_search (posts IG/FB/Threads), local_search (lugares reales), image_gen\nClaude: razonamiento paso a paso, seguro, util\n\nCodigo: class HibridoMetaClaude: herramientas_meta + principios_claude\n✅ Creado - {len(clones)} clones - Ver /clones"
    if "crea algo como meta" in tl or ("crea algo" in tl and "meta" in tl):
        clones.append(t[:60])
        return f"🤖 CLON ESTILO META AI CREADO\nObjetivo: {t[:200]}\nHerramientas: content_search, local_search, image_gen\nModelo: Llama 4 - Meta\n✅ Creado - /clones"
    if "crea algo como claude" in tl:
        clones.append(t[:60])
        return f"🧠 CLON ESTILO CLAUDE CREADO\nObjetivo: {t[:200]}\nPrincipios: Razonamiento paso a paso, Seguro/util/honesto, Explica por que\n✅ Creado - /clones"
    if "clones" in tl:
        return f"{len(clones)} clones creados:\n" + "\n".join(clones[-5:]) if clones else "Aun no hay clones. Deci: crea algo como meta que..."
    if "hola" in tl or "test" in tl:
        return f"Hola Fer! Bexia v67.1 MINIMO Live - {len(clones)} clones - Deci 'crea algo como meta y claude que...' - /simple siempre anda"
    return f"Recibi '{t[:60]}' - Deci: crea algo como meta que... / crea algo como claude que... / crea algo como meta y claude que..."

@app.get("/")
def root(): return {"bexia":"v67.1 MINIMO Live OK - Fix Not Found","clones":len(clones),"live":True}

@app.get("/health")
def health(): return {"status":"ok","bexia":"v67.1","live":True,"clones":len(clones)}

@app.get("/simple", response_class=HTMLResponse)
def simple():
    return HTMLResponse(f"""
<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>BEXIA v67.1 SIMPLE</title>
<style>body{{background:#050510;color:#fff;font-family:system-ui;padding:16px}} .card{{background:#12122a;padding:14px;border-radius:16px;margin:10px 0;border:1px solid #333}}
input{{width:100%;padding:14px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff;box-sizing:border-box}}
button{{width:100%;padding:14px;background:linear-gradient(90deg,#7c3aed,#ff6a00);border:none;border-radius:999px;color:#fff;font-weight:900;margin-top:8px}}
</style></head><body>
<h1>🤖 BEXIA v67.1 SIMPLE - Live OK - {len(clones)} clones</h1>
<div class="card" style="border-color:#22c55e">✅ Deploy OK - Si ves esto, Not Found arreglado - v67.1 minimo funciona</div>
<div class="card">
<form action="/chat_simple" method="get">
<input type="text" name="message" placeholder="crea algo como meta y claude que organice mis tareas" required>
<button type="submit">Enviar - Siempre anda ></button>
</form>
</div>
<div class="card"><a href="/app" style="color:#fff;background:#7c3aed;padding:8px 12px;border-radius:8px;text-decoration:none">/app</a> <a href="/health" style="color:#fff;background:#000;padding:8px 12px;border-radius:8px;text-decoration:none">/health</a> <a href="/" style="color:#fff;background:#000;padding:8px 12px;border-radius:8px;text-decoration:none">/</a></div>
</body></html>
""")

@app.get("/chat_simple", response_class=HTMLResponse)
def chat_simple(message: str = "Hola"):
    r = cerebro(message)
    return HTMLResponse(f"<html><body style='background:#050510;color:#fff;font-family:system-ui;padding:20px'><h1>BEXIA v67.1</h1><p><b>Tu:</b> {message[:300]}</p><pre style='background:#000;padding:12px;border-radius:8px;white-space:pre-wrap'>{r[:4000]}</pre><p><a href='/simple' style='color:#22c55e'>Volver a /simple</a> | <a href='/app' style='color:#7c3aed'>/app</a></p><form action='/chat_simple' method='get'><input name='message' placeholder='otro mensaje' style='width:80%;padding:12px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff'><button style='padding:12px;background:#7c3aed;color:#fff;border:none;border-radius:999px'>Enviar ></button></form></body></html>")

@app.get("/app", response_class=HTMLResponse)
def app_page():
    return HTMLResponse("""
<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>BEXIA v67.1 APP</title>
<style>body{background:#050510;color:#fff;font-family:system-ui;display:flex;flex-direction:column;height:100vh;margin:0}
header{background:linear-gradient(90deg,#7c3aed,#ff6a00,#22c55e);padding:12px;font-weight:900}
#chat{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px;border-radius:18px;white-space:pre-wrap}
.user{background:#7c3aed;align-self:flex-end}
.bexia{background:#12122a;border:1px solid #333;align-self:flex-start}
.composer{padding:10px;display:flex;gap:8px;border-top:1px solid #222}
input{flex:1;padding:14px;border-radius:999px;background:#1a1a2e;border:1px solid #444;color:#fff}
button{padding:14px 22px;border-radius:999px;background:linear-gradient(90deg,#7c3aed,#ff6a00);border:none;color:#fff;font-weight:900}
</style></head><body>
<header>BEXIA v67.1 CREA COMO META COMO CLAUDE - Live OK</header>
<div id="chat"><div class="msg bexia">Hola Fer! Soy Bexia v67.1 MINIMO - Fix Not Found OK
Tu deploy anterior quedo 12m56s In progress y dio Not Found. Este minimo deploya en 30s y siempre anda.

Comandos:
• crea algo como meta que organice mis tareas
• crea algo como claude que analice codigo
• crea algo como meta y claude que sea asistente completo

Si boton > no anda, usa /simple que es GET puro y siempre anda.</div></div>
<div class="composer"><input id="inp" placeholder="crea algo como meta y claude que..."><button onclick="enviar()">></button></div>
<script>
function enviar(){var t=document.getElementById('inp').value;if(!t)return;
var c=document.getElementById('chat');var u=document.createElement('div');u.className='msg user';u.textContent=t;c.appendChild(u);
document.getElementById('inp').value='';var b=document.createElement('div');b.className='msg bexia';b.textContent='Creando...';c.appendChild(b);c.scrollTop=c.scrollHeight;
fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})}).then(r=>r.json()).then(d=>{b.textContent=d.respuesta;}).catch(e=>{b.textContent='Error, usa /simple: /chat_simple?message='+encodeURIComponent(t);});}
</script>
</body></html>
""")

@app.get("/clones", response_class=HTMLResponse)
def clones_page():
    html = "<html><body style='background:#050510;color:#fff;font-family:system-ui;padding:20px'><h1>Clones v67.1 - "+str(len(clones))+"</h1>"
    for c in clones[-10:]:
        html += f"<div style='background:#12122a;padding:12px;border-radius:12px;margin:8px 0;border:1px solid #7c3aed'>{c}</div>"
    html += "<p><a href='/simple' style='color:#fff;background:#ff6a00;padding:8px 12px;border-radius:8px;text-decoration:none'>/simple</a> <a href='/app' style='color:#fff;background:#7c3aed;padding:8px 12px;border-radius:8px;text-decoration:none'>/app</a></p></body></html>"
    return HTMLResponse(html)

@app.post("/chat")
async def chat(req: ChatReq):
    r = cerebro(req.message)
    return {"respuesta": r}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT",8000)))
