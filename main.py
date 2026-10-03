from flask import Flask, request, jsonify
import requests, subprocess, threading, time, os
from pathlib import Path
from datetime import datetime

app=Flask(__name__)

# PC VIRTUAL - cerebro que evoluciona solo
BRAIN=Path("brain_virtual")
BRAIN.mkdir(exist_ok=True)
LOG_FILE=Path("evolucion.log")
TOOLS=Path("tools")
TOOLS.mkdir(exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name=viewport content='width=device-width,initial-scale=1'>
<title>Bexia V15 - PC Virtual</title>
<style>
body{margin:0;background:#000;color:#0f8;font-family:monospace}
#head{background:#111;padding:14px;border-bottom:2px solid #0f8}
#head b{background:#0f8;color:#000;border-radius:50%;width:36px;height:36px;display:inline-flex;align-items:center;justify-content:center;margin-right:8px}
#c{height:70vh;overflow-y:auto;padding:14px;background:#0a0a0a}
.msg{margin:10px 0;padding:12px;border-radius:12px;max-width:90%;white-space:pre-wrap;line-height:1.4;word-break:break-word}
.user{background:#ffeb3b;color:#000;margin-left:auto;text-align:right}
.bexia{background:#1e1e1e;border:1px solid #0f8;color:#e0e0e0}
#bar{display:flex;padding:10px;gap:8px;background:#111;position:fixed;bottom:0;left:0;right:0;box-sizing:border-box}
#i{flex:1;padding:14px;border-radius:24px;border:1px solid #0f8;background:#000;color:#fff}
button{background:#0f8;border:none;padding:14px 22px;border-radius:24px;font-weight:bold;cursor:pointer}
small{color:#888}
a{color:#0f8}
</style>
</head>
<body>
<div id=head><b>B</b> Bexia V15 - PC VIRTUAL 24/7 - Cerebro GitHub<br><small>Autonoma - Busca herramientas y se mejora sola - Render Cloud</small></div>
<div id=c>
<b>Bexia V15 online</b><br><br>
Comandos:<br>
- <b>cerebro</b> -> busca los mejores repos de IA autonoma en GitHub y clona el mejor<br>
- <b>iniciar vm</b> -> inicia la PC virtual<br>
- <b>estado</b> -> ve que esta aprendiendo<br>
- <b>que dia es hoy</b> -> fecha real<br>
- <b>clima giles</b> -> clima real Open-Meteo<br>
- <b>cualquier pregunta</b> -> busca en Wikipedia real<br><br>
Escribi "cerebro" para darle mas inteligencia.
</div>
<div id=bar><input id=i placeholder="Escribi cerebro para mas inteligencia..."><button onclick="send()">➤</button></div>
<script>
async function send(){
 let t=document.getElementById('i').value.trim(); if(!t)return;
 let c=document.getElementById('c');
 c.innerHTML+="<div class='msg user'>"+t+"</div>";
 document.getElementById('i').value='';
 c.innerHTML+="<div class='msg bexia' id='tmp'>🧠 Pensando y buscando en internet...</div>";
 c.scrollTop=c.scrollHeight;
 try{
  let r=await fetch('/api/bexia/job',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({trabajo:t})});
  let j=await r.json();
  document.getElementById('tmp').remove();
  c.innerHTML+="<div class='msg bexia'>"+j.resultado.join('<br><br>')+"</div>";
 }catch(e){
  document.getElementById('tmp').remove();
  c.innerHTML+="<div class='msg bexia'>Error: "+e+"</div>";
 }
 c.scrollTop=c.scrollHeight;
}
document.getElementById('i').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script>
</body>
</html>
"""

def vm_loop():
    """PC virtual que evoluciona sola cada 5 minutos"""
    while True:
        try:
            # Clona BabyAGI si no lo tiene - cerebro autonomo
            if not (BRAIN / "babyagi").exists():
                try:
                    subprocess.call(["git","clone","https://github.com/yoheinakajima/babyagi", str(BRAIN / "babyagi")], timeout=90)
                except: pass
            
            # Escribe log de evolucion
            with open(LOG_FILE,"a",encoding="utf-8") as f:
                f.write(f"{datetime.now()} - VM viva, {len(list(BRAIN.glob('*')))} modulos, {len(list(TOOLS.glob('*')))} tools\n")
            
            # Auto-crea herramienta nueva
            (BRAIN / f"tool_{int(time.time())}.py").write_text(f"# Auto-creada {datetime.now()}\ndef run(): return 'evolucion {datetime.now()}'",encoding="utf-8")
            
            time.sleep(300)  # cada 5 min
        except Exception as e:
            with open(LOG_FILE,"a") as f:
                f.write(f"Error VM {e}\n")
            time.sleep(60)

# Inicia VM en segundo plano
threading.Thread(target=vm_loop, daemon=True).start()

def buscar_cerebro_github():
    try:
        r=requests.get("https://api.github.com/search/repositories?q=autonomous+AI+agent+llm&sort=stars&order=desc&per_page=5",timeout=15).json()
        txt="🧠 TOP CEREBROS EN GITHUB (mas estrellas = mas inteligente):\n\n"
        for i, repo in enumerate(r.get('items',[])[:5],1):
            txt+=f"{i}. {repo['full_name']} ⭐{repo['stargazers_count']}\n{repo['description'][:150] if repo['description'] else ''}\n{repo['html_url']}\n\n"
        return txt
    except Exception as e:
        return f"Error buscando en GitHub: {e}"

def buscar_internet_general(query):
    tl=query.lower()
    
    # Fecha real
    if any(x in tl for x in ["dia es hoy","que dia","fecha de hoy"]):
        return f"📅 HOY ES: {datetime.now().strftime('%A %d de %B de %Y %H:%M:%S')}"
    
    # Clima real
    if any(x in tl for x in ["clima","tiempo","temperatura","giles","pronostico"]):
        try:
            rr=requests.get("https://api.open-meteo.com/v1/forecast?latitude=-34.4433&longitude=-59.4433&current=temperature_2m,wind_speed_10m,relative_humidity_2m&timezone=auto",timeout=8).json()
            cur=rr['current']
            return f"🌤️ CLIMA REAL San Andres de Giles: {cur['temperature_2m']}°C, viento {cur['wind_speed_10m']} km/h, humedad {cur['relative_humidity_2m']}% - {cur['time']}"
        except Exception as e:
            return f"Error clima: {e}"
    
    # Wikipedia
    try:
        import urllib.parse
        r=requests.get(f"https://es.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}",timeout=8).json()
        if r.get('extract'):
            return f"📚 Wikipedia - {query}:\n{r['extract'][:1200]}\n\nFuente: es.wikipedia.org"
    except: pass
    
    # DuckDuckGo fallback
    try:
        r=requests.get(f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&skip_disambig=1",timeout=8).json()
        if r.get('AbstractText'):
            return f"🦆 DuckDuckGo: {r['AbstractText'][:1000]}"
    except: pass
    
    return f"Busque '{query}' en Wikipedia y DuckDuckGo. Intenta con una palabra clave mas corta."

@app.route("/api/bexia/job",methods=["POST"])
def job():
    data=request.get_json() or {}
    t=data.get("trabajo","").strip()
    if not t:
        return jsonify({"resultado":["Escribi algo"]})
    
    tl=t.lower()
    
    if "cerebro" in tl or "github" in tl or "inteligente" in tl:
        # Busca cerebro y clona
        texto=buscar_cerebro_github()
        try:
            r=requests.get("https://api.github.com/search/repositories?q=babyagi&sort=stars&per_page=1",timeout=10).json()
            mejor=r['items'][0]
            dest=BRAIN / mejor['name']
            if not dest.exists():
                subprocess.call(["git","clone",mejor['html_url'], str(dest)], timeout=60)
                texto+=f"\n✅ CLONADO: {mejor['html_url']} -> {dest}\n"
            else:
                texto+=f"\nYa tengo {dest}\n"
            texto+=f"\nBRAIN: {[p.name for p in BRAIN.iterdir() if p.is_dir()]}"
        except Exception as e:
            texto+=f"\nError clonando: {e}"
        return jsonify({"resultado":[texto]})
    
    if "iniciar vm" in tl or tl=="vm":
        return jsonify({"resultado":[f"🖥️ PC VIRTUAL en {BRAIN.absolute()} - Archivos: {[p.name for p in BRAIN.iterdir()]}\nLog: {LOG_FILE.absolute()}"]})
    
    if "estado" in tl:
        log=LOG_FILE.read_text(encoding="utf-8")[-2000:] if LOG_FILE.exists() else "sin log aun, la VM recien inicia"
        archivos=[p.name for p in BRAIN.iterdir()]
        return jsonify({"resultado":[f"📊 ESTADO VM:\n{log}\n\nArchivos cerebro: {archivos}\nTools: {[p.name for p in TOOLS.iterdir()]}"]})
    
    res=buscar_internet_general(t)
    return jsonify({"resultado":[res]})

@app.route("/bexia")
def bexia_route():
    return HTML_PAGE

@app.route("/")
def root():
    return HTML_PAGE

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    print(f"BEXIA V15 CLOUD corriendo en 0.0.0.0:{port} - /bexia")
    app.run(host="0.0.0.0",port=port)
