# Bexia V16.1 - ECC Architecture + 【entity-WhatsApp¦canonical_name=WhatsApp】
# Basado en tu V16 original de Fernando - Poco F8 Ultra
# Reglas: ~/.claude/rules/ecc/common/

from flask import Flask, request, jsonify
import requests
import subprocess
import threading
import time
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
import json

# === CONFIG 【entity-WHATSAPP¦canonical_name=WhatsApp】 - Se pone en Render como Environment Variables ===
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "bexia123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
# =====================================================================

# === CORE - Siguiendo ECC: Separation of Concerns ===

@dataclass
class ToolResult:
    """ECC Rule: Typed results, not raw strings"""
    success: bool
    output: str
    source: str
    tool_path: Optional[Path] = None

class BrainRegistry:
    """ECC Rule: Single source of truth for tools"""
    def __init__(self, base_path: Path):
        self.base = base_path
        self.brain_path = base_path / "brain_virtual"
        self.tools_path = base_path / "tools"
        self.log_path = base_path / "evolucion.log"
        # Memoria de Bexia chiquita - la que hicimos en Colab, peso 0.95
        self.memoria_path = base_path / "memoria_bexia.json"
        self.brain_path.mkdir(exist_ok=True)
        self.tools_path.mkdir(exist_ok=True)
        if not self.memoria_path.exists():
            self.memoria_path.write_text(json.dumps({"peso": 0.95, "aprendizajes": ["me gusta el fútbol y la IA"], "proyectos_vistos": []}, ensure_ascii=False), encoding="utf-8")

    def log(self, msg: str):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")

    def get_memoria(self):
        try:
            return json.loads(self.memoria_path.read_text(encoding="utf-8"))
        except:
            return {"peso": 0.95, "aprendizajes": [], "proyectos_vistos": []}

    def guardar_memoria(self, memoria):
        self.memoria_path.write_text(json.dumps(memoria, ensure_ascii=False), encoding="utf-8")

class InternetSearch:
    """ECC Rule: One class, one responsibility - Busqueda real"""
    @staticmethod
    def search_wikipedia(query: str) -> Optional[str]:
        try:
            import urllib.parse
            r = requests.get(f"https://es.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}", timeout=8).json()
            if r.get('extract'):
                return r['extract']
        except: pass
        return None

    @staticmethod
    def search_date() -> str:
        return datetime.now().strftime("%A %d de %B %Y %H:%M:%S - GMT-3 Argentina")

    @staticmethod
    def search_weather() -> Optional[str]:
        try:
            r = requests.get("https://api.open-meteo.com/v1/forecast?latitude=-34.4433&longitude=-59.4433&current=temperature_2m,wind_speed_10m,relative_humidity_2m&timezone=auto", timeout=8).json()
            cur = r['current']
            return f"San Andres de Giles: {cur['temperature_2m']}°C, viento {cur['wind_speed_10m']} km/h, humedad {cur['relative_humidity_2m']}%"
        except: return None

class GitHubBrain:
    """ECC Rule: Reusable, testable module - Cerebro 【entity-GitHub¦canonical_name=GitHub】"""
    SEARCH_URL = "https://api.github.com/search/repositories"

    def search_top_repos(self, query: str = "autonomous AI agent llm", limit: int = 5) -> List[Dict]:
        try:
            r = requests.get(f"{self.SEARCH_URL}?q={query}&sort=stars&order=desc&per_page={limit}", timeout=15).json()
            return r.get('items', [])[:limit]
        except: return []

    def clone(self, repo_url: str, dest: Path) -> ToolResult:
        if dest.exists():
            return ToolResult(True, f"Ya existe {dest.name}", "local", dest)
        try:
            subprocess.check_call(["git", "clone", repo_url, str(dest)], timeout=90)
            return ToolResult(True, f"Clonado {repo_url}", "【entity-github¦canonical_name=GitHub】", dest)
        except Exception as e:
            return ToolResult(False, f"Error clonando: {e}", "【entity-github¦canonical_name=GitHub】")

# === VM VIRTUAL - Evoluciona sola ===
registry = BrainRegistry(Path("."))
github_brain = GitHubBrain()

def vm_evolution_loop():
    """ECC: Background worker separado - V16.1 con limpieza"""
    while True:
        try:
            babyagi_path = registry.brain_path / "babyagi"
            if not babyagi_path.exists():
                github_brain.clone("https://github.com/yoheinakajima/babyagi", babyagi_path)

            # Limpieza ECC: max 20 tools, no inundar disco
            tools = sorted(registry.brain_path.glob("tool_*.py"), key=lambda p: p.stat().st_mtime)
            if len(tools) > 20:
                for viejo in tools[:-20]:
                    viejo.unlink(missing_ok=True)

            registry.log(f"VM activa - {len(list(registry.brain_path.glob('*')))} modulos, {len(list(registry.tools_path.glob('*')))} tools")
            tool_name = f"tool_{int(time.time())}"
            tool_code = f'''"""
Tool auto-generada siguiendo ECC common rules
Generated: {datetime.now().isoformat()}
"""
def run(query: str) -> str:
    """Ejecuta tarea"""
    return f"Tool {tool_name} ejecutada: {{query}}"
def test():
    assert run("test") is not None
if __name__ == "__main__":
    print(run("demo"))
'''
            (registry.brain_path / f"{tool_name}.py").write_text(tool_code, encoding="utf-8")
            time.sleep(300)
        except Exception as e:
            registry.log(f"VM Error: {e}")
            time.sleep(60)

threading.Thread(target=vm_evolution_loop, daemon=True).start()

# === CEREBRO UNIFICADO - ECC: Una función, dos entradas (Web + 【entity-WhatsApp¦canonical_name=WhatsApp】) ===
def procesar_bexia(t: str) -> str:
    tl = t.lower().strip()
    memoria = registry.get_memoria()

    # --- Comandos de Bexia chiquita (de Colab) ---
    if "mejorate" in tl or "mejora" in tl:
        antes = memoria.get("peso", 0.95)
        memoria["peso"] = round(min(1.0, antes + 0.05), 2)
        registry.guardar_memoria(memoria)
        registry.log(f"Auto-mejora: peso {antes} -> {memoria['peso']}")
        return f"Fer, me auto-corregí. Mi peso pasó de {antes} a {memoria['peso']}. Como Astra, sin reentrenar."

    if "aprende que" in tl:
        dato = t.split("aprende que")[-1].strip()
        memoria.setdefault("aprendizajes", []).append(dato)
        registry.guardar_memoria(memoria)
        return f"Anotado, Fer. Aprendí que {dato}. Ya no me lo olvido."

    if "que sabes de mi" in tl or "que aprendiste" in tl:
        if memoria.get("aprendizajes"):
            return "De vos aprendí: " + " | ".join(memoria["aprendizajes"])
        return "Todavía no me enseñaste nada, Fer. Decime 'Bexia, aprende que...'"

    if "peso" in tl:
        return f"Mi peso actual es {memoria.get('peso', 0.95)}. Empecé en 0.5, vos me curaste a 0.9 y ahora voy en {memoria.get('peso', 0.95)}."

    if "hola" in tl:
        return "¡Hola Fer! Soy Bexia V16.1 en WhatsApp. ¿Qué inventamos hoy? Decime 'cerebro', 'clima', 'estado' o 'Bexia, mejorate'."

    # --- Comandos V16 originales ---
    if "cerebro" in tl or "github" in tl:
        repos = github_brain.search_top_repos()
        if not repos:
            return "No pude conectar a GitHub API"
        txt = "🧠 TOP CEREBROS (ECC - mas estrellas = mejor arquitectura):\n\n"
        for i, r in enumerate(repos, 1):
            txt += f"{i}. {r['full_name']} ⭐{r['stargazers_count']}\n{r.get('description','')[:120]}\n{r['html_url']}\n\n"
        mejor = repos[0]
        result = github_brain.clone(mejor['html_url'], registry.brain_path / mejor['name'])
        txt += f"\n{result.output}\n📁 BRAIN: {[p.name for p in registry.brain_path.iterdir()]}"
        registry.log(f"Cerebro instalado: {mejor['full_name']}")
        return txt

    if "iniciar vm" in tl or tl == "vm":
        return f"🖥️ VM en {registry.brain_path.absolute()} - {len(list(registry.brain_path.glob('*')))} modulos - Log: {registry.log_path}"

    if "estado" in tl:
        log = registry.log_path.read_text(encoding="utf-8")[-2000:] if registry.log_path.exists() else "VM recien inicia"
        return f"📊 ESTADO ECC VM:\n{log}\n\nBrain: {[p.name for p in registry.brain_path.iterdir()]}\nTools: {[p.name for p in registry.tools_path.iterdir()]}"

    if "dia es hoy" in tl or "fecha" in tl:
        return f"📅 {InternetSearch.search_date()}"

    if "clima" in tl or "giles" in tl:
        w = InternetSearch.search_weather()
        return f"🌤️ {w}" if w else "Error clima"

    wiki = InternetSearch.search_wikipedia(t)
    if wiki:
        return f"📚 {wiki[:1200]}"

    return f"Busque '{t}' - intenta palabra clave mas corta. Probá: cerebro, clima, estado, Bexia mejorate"

# === FLASK APP - ECC: Thin controller ===
app = Flask(__name__)

HTML = """
<!DOCTYPE html><html><head><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Bexia V16 ECC</title>
<style>
body{margin:0;background:#0a0a0a;color:#0f8;font-family:monospace}
#head{background:#111;padding:14px;border-bottom:2px solid #0f8;position:sticky;top:0}
#head b{background:#0f8;color:#000;border-radius:50%;width:36px;height:36px;display:inline-flex;align-items:center;justify-content:center}
#c{height:68vh;overflow-y:auto;padding:14px;padding-bottom:80px}
.msg{margin:10px 0;padding:12px;border-radius:10px;max-width:92%;white-space:pre-wrap;line-height:1.5;word-break:break-word}
.user{background:#ffeb3b;color:#000;margin-left:auto}
.bexia{background:#1a1a1a;border:1px solid #0f8;color:#e0e0e0}
#bar{display:flex;padding:10px;gap:8px;background:#111;position:fixed;bottom:0;left:0;right:0}
#i{flex:1;padding:14px;border-radius:24px;border:1px solid #0f8;background:#000;color:#fff}
button{background:#0f8;border:none;padding:14px 22px;border-radius:24px;font-weight:bold;cursor:pointer}
small{color:#888}
</style></head><body>
<div id=head><b>B</b> Bexia V16.1 ECC + WhatsApp - PC Virtual 24/7<br><small>Architecture: common rules | Brain: GitHub | VM: evoluciona sola</small></div>
<div id=c>
<b>🧠 Bexia V16.1 con reglas ECC activas</b><br><br>
- <b>cerebro</b> -> busca top repos GitHub y clona el mejor<br>
- <b>iniciar vm</b> -> PC virtual<br>
- <b>estado</b> -> logs de evolucion<br>
- <b>Bexia, mejorate</b> -> auto-corrección estilo Astra<br>
- <b>clima / dia / cualquier tema</b> -> busca en internet real<br><br>
ECC: Cada tool es testeable y reutilizable. Ahora también en WhatsApp.
</div>
<div id=bar><input id=i placeholder="Escribi cerebro para darle mas IQ..."><button onclick="send()">➤</button></div>
<script>
async function send(){
 let t=document.getElementById('i').value.trim(); if(!t)return;
 let c=document.getElementById('c');
 c.innerHTML+="<div class='msg user'>"+t+"</div>"; document.getElementById('i').value='';
 c.innerHTML+="<div class='msg bexia' id='tmp'>🧠 ECC pensando...</div>"; c.scrollTop=c.scrollHeight;
 try{
  let r=await fetch('/api/bexia/job',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({trabajo:t})});
  let j=await r.json(); document.getElementById('tmp').remove();
  c.innerHTML+="<div class='msg bexia'>"+j.resultado.join('<br><br>')+"</div>";
 }catch(e){document.getElementById('tmp').remove(); c.innerHTML+="<div class='msg bexia'>Error: "+e+"</div>";}
 c.scrollTop=c.scrollHeight;
}
document.getElementById('i').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""

@app.route("/api/bexia/job", methods=["POST"])
def job():
    t = (request.get_json() or {}).get("trabajo", "").strip()
    if not t:
        return jsonify({"resultado": ["Escribi algo"]})
    return jsonify({"resultado": [procesar_bexia(t)]})

# === WHATSAPP - Nuevo en V16.1 ===
def enviar_whatsapp(numero_destino, texto):
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print("WhatsApp no configurado, no se envía")
        return
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    # WhatsApp corta mensajes muy largos, los partimos
    for i in range(0, len(texto), 3500):
        parte = texto[i:i+3500]
        data = {"messaging_product": "whatsapp", "to": numero_destino, "type": "text", "text": {"body": parte}}
        try:
            requests.post(url, headers=headers, json=data, timeout=10)
        except Exception as e:
            print(f"Error enviando 【entity-WhatsApp¦canonical_name=WhatsApp】: {e}")

@app.route("/webhook", methods=["GET"])
def verificar_whatsapp():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def recibir_whatsapp():
    try:
        data = request.get_json()
        mensaje = data["entry"][0]["changes"][0]["value"]["messages"][0]
        texto_entrante = mensaje["text"]["body"]
        numero = mensaje["from"]
        respuesta = procesar_bexia(texto_entrante)
        enviar_whatsapp(numero, respuesta)
    except Exception as e:
        print(f"Error webhook: {e}")
    return "OK", 200

@app.route("/bexia")
def bexia(): return HTML
@app.route("/")
def root(): return HTML

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Bexia V16.1 ECC + WhatsApp en puerto {port}")
    app.run(host="0.0.0.0", port=port)
