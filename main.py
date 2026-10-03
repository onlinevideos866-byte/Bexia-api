from flask import Flask, request, jsonify
import requests, subprocess, threading, time, os
from pathlib import Path
from datetime import datetime

app=Flask(__name__)
BRAIN=Path("brain_virtual")
BRAIN.mkdir(exist_ok=True)
LOG_FILE=Path("evolucion.log")

HTML_PAGE = """
<!DOCTYPE html><html><head><meta name=viewport content='width=device-width,initial-scale=1'>
<style>
body{margin:0;background:#000;color:#0f8;font-family:monospace}
#head{background:#111;padding:12px;border-bottom:2px solid #0f8}
#c{height:72vh;overflow:auto;padding:12px;background:#0a0a0a}
.msg{margin:8px 0;padding:12px;border-radius:12px;max-width:90%;white-space:pre-wrap}
.user{background:#ffeb3b;color:#000;margin-left:auto}
.bexia{background:#1e1e1e;border:1px solid #0f8;color:#e0e0e0}
#bar{display:flex;padding:10px;gap:8px;background:#111;position:fixed;bottom:0;width:100%;box-sizing:border-box}
#i{flex:1;padding:14px;border-radius:24px;border:1px solid #0f8;background:#000;color:#fff}
button{background:#0f8;border:none;padding:14px 20px;border-radius:24px;font-weight:bold}
</style></head><body>
<div id=head>Bexia V14 NUBE 24/7 - PC Virtual<br><small>Evoluciona sola - Busca cerebros en GitHub</small></div>
<div id=c>Comandos:<br>- iniciar vm<br>- estado<br>- cerebro (busca repos)<br>- que dia es hoy<br>- clima giles<br>- cualquier pregunta</div>
<div id=bar><input id=i placeholder="Escribi cerebro..."><button onclick="send()">Enviar</button></div>
<script>
async function send(){
 let t=document.getElementById('i').value; if(!t)return;
 let c=document.getElementById('c');
 c.innerHTML+="<div class='msg user'>"+t+"</div>"; document.getElementById('i').value='';
 c.innerHTML+="<div class='msg bexia' id='tmp'>Buscando...</div>"; c.scrollTop=9999;
 let r=await fetch('/api/bexia/job',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({trabajo:t})});
 let j=await r.json(); document.getElementById('tmp').remove();
 c.innerHTML+="<div class='msg bexia'>"+j.resultado.join('<br><br>')+"</div>"; c.scrollTop=9999;
}
document.getElementById('i').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""

def vm_loop():
    while True:
        try:
            if not (BRAIN / "babyagi").exists():
                subprocess.call(["git","clone","https://github.com/yoheinakajima/babyagi", str(BRAIN / "babyagi")], timeout=90)
            with open(LOG_FILE,"a") as f:
                f.write(f"{datetime.now()} - VM viva, {len(list(BRAIN.glob('*')))} modulos\n")
            (BRAIN / f"tool_{int(time.time())}.py").write_text(f"# auto {datetime.now()}\ndef run(): return 'ok'")
            time.sleep(300)
        except:
            time.sleep(60)

threading.Thread(target=vm_loop, daemon=True).start()

def buscar_cerebro():
    try:
        r=requests.get("https://api.github.com/search/repositories?q=autonomous+AI+agent&sort=stars&per_page=5",timeout=10).json()
        txt="TOP CEREBROS GITHUB:\n\n"
        for repo in r.get('items',[])[:5]:
            txt+=f"{repo['full_name']} - {repo['stargazers_count']} stars\n{repo['description'][:120]}\n{repo['html_url']}\n\n"
        return txt
    except Exception as e:
        return str(e)

def buscar_general(q):
    tl=q.lower()
    if "dia es hoy" in tl or "fecha" in tl:
        return f"HOY: {datetime.now().strftime('%A %d de %B %Y %H:%M:%S')}"
    if "clima" in tl or "giles" in tl:
        try:
            rr=requests.get("https://api.open-meteo.com/v1/forecast?latitude=-34.4433&longitude=-59.4433&current=temperature_2m,wind_speed_10m&timezone=auto",timeout=6).json()
            return f"Clima Giles: {rr['current']}"
        except Exception as e:
            return f"Error clima {e}"
    try:
        import urllib.parse
        r=requests.get(f"https://es.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(q)}",timeout=6).json()
        if r.get('extract'):
            return r['extract'][:900]
    except: pass
    return f"Busque {q} en internet"

@app.route("/api/bexia/job",methods=["POST"])
def job():
    t=(request.get_json() or {}).get("trabajo","")
    tl=t.lower()
    if "iniciar vm" in tl:
        return jsonify({"resultado":[f"PC VIRTUAL en {BRAIN.absolute()} - {list(BRAIN.glob('*'))}"]})
    if "estado" in tl:
        log=LOG_FILE.read_text()[-1500:] if LOG_FILE.exists() else "sin log"
        return jsonify({"resultado":[f"LOG: {log} - BRAIN: {[p.name for p in BRAIN.iterdir()]}"]})
    if "cerebro" in tl:
        return jsonify({"resultado":[buscar_cerebro()]})
    return jsonify({"resultado":[buscar_general(t)]})

@app.route("/bexia")
def b(): return HTML_PAGE
@app.route("/")
def root(): return HTML_PAGE

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
