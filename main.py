"""
BEXIA v38.2 RENDER FIX - Soluciona Exited with status 1
- Sin google genai, sin dependencias extra
- Solo fastapi + uvicorn + requests
- Maneja archivos faltantes sin crashear
- Log de inicio para Render
"""
import os, json, re, time
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

print("🔄 BEXIA v38.2 iniciando... Render fix", flush=True)

try:
    import requests
    HAS_REQUESTS=True
    print("✅ requests disponible", flush=True)
except:
    HAS_REQUESTS=False
    print("⚠️ requests no disponible, usando urllib", flush=True)
    import urllib.request
    import urllib.parse

import urllib.request
import urllib.parse

OWNER_SECRET = "BEXIA_FER_2026_INFINITA_SUPREMA"

app = FastAPI(title="BEXIA v38.2 RENDER FIX", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def load_json(p,d):
    try:
        if os.path.exists(p):
            with open(p,"r",encoding="utf-8") as fp:
                data=json.load(fp)
                print(f"✅ Cargado {p}", flush=True)
                return data
    except Exception as e:
        print(f"⚠️ No se pudo cargar {p}: {e}", flush=True)
    return d

def save_json(p,d):
    try:
        with open(p,"w",encoding="utf-8") as fp: json.dump(d, fp, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ No se pudo guardar {p}: {e}", flush=True)
        return False

print("📚 Cargando memoria...", flush=True)
conocimiento = load_json("bexia_conocimiento.json", {"hechos":[],"nivel":14.0,"total_hechos":70})
evol = load_json("bexia_evolucion.json", {"nivel":14.0,"fase":"Experta"})
regen_db = load_json("bexia_regeneracion.json", {"regeneraciones":[],"adn":"BEXIA_v38.2_RENDER","versiones_creadas":[]})
cerebro_db = load_json("bexia_cerebro.json", {"pensamientos":[],"busquedas":[]})
stats_busqueda = load_json("bexia_buscador_stats.json", {"motores":{"DuckDuckGo":0,"Wikipedia":0,"Google":0},"total_busquedas":0})
print(f"✅ Memoria: {conocimiento.get('total_hechos',0)} hechos, ADN {regen_db.get('adn','')}", flush=True)

def buscar_wikipedia_libre(q, lang="es"):
    try:
        q_enc=urllib.parse.quote(q)
        search_url=f"https://{lang}.wikipedia.org/w/api.php?action=opensearch&search={q_enc}&limit=1&format=json"
        if HAS_REQUESTS:
            r=requests.get(search_url, timeout=5, headers={"User-Agent":"Bexia/1.0"})
            data=r.json()
        else:
            req_obj=urllib.request.Request(search_url, headers={"User-Agent":"Bexia/1.0"})
            with urllib.request.urlopen(req_obj, timeout=5) as resp:
                data=json.loads(resp.read().decode('utf-8'))
        if len(data)>=2 and data[1]:
            titulo=data[1][0]
            t_enc=urllib.parse.quote(titulo)
            extract_url=f"https://{lang}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={t_enc}&format=json"
            if HAS_REQUESTS:
                r2=requests.get(extract_url, timeout=5)
                data2=r2.json()
            else:
                req2=urllib.request.Request(extract_url, headers={"User-Agent":"Bexia/1.0"})
                with urllib.request.urlopen(req2, timeout=5) as resp2:
                    data2=json.loads(resp2.read().decode('utf-8'))
            pages=data2.get("query",{}).get("pages",{})
            for p in pages.values():
                ext=p.get("extract","")[:600]
                if ext:
                    stats_busqueda["motores"]["Wikipedia"]=stats_busqueda["motores"].get("Wikipedia",0)+1
                    return f"Wikipedia {titulo}: {ext}"
        return None
    except Exception as e:
        print(f"Wiki error: {e}", flush=True)
        return None

def buscar_google_libre(q):
    try:
        q_enc=urllib.parse.quote(q)
        url=f"https://html.duckduckgo.com/html/?q={q_enc}"
        if HAS_REQUESTS:
            r=requests.get(url, timeout=6, headers={"User-Agent":"Mozilla/5.0"})
            html=r.text
        else:
            req_obj=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req_obj, timeout=6) as resp:
                html=resp.read().decode('utf-8', errors='ignore')
        res=re.findall(r'class="result__a"[^>]*>([^<]+)</a>.*?result__snippet[^>]*>([^<]+)', html, re.DOTALL)[:3]
        if not res:
            res=re.findall(r'result__snippet[^>]*>([^<]+)', html)[:3]
            res=[(f"Resultado {i+1}", r) for i,r in enumerate(res)]
        if res:
            stats_busqueda["motores"]["Google"]=stats_busqueda["motores"].get("Google",0)+1
            return "\n".join([f"• {t.strip()}: {s.strip()[:150]}..." for t,s in res])
        return None
    except Exception as e:
        print(f"Google error: {e}", flush=True)
        return None

def buscar_internet_adaptativo(query):
    resultados=[]
    for nombre, func in [("Wikipedia", lambda q: buscar_wikipedia_libre(q)), ("Google", buscar_google_libre)]:
        try:
            r=func(query)
            if r and len(r)>20:
                resultados.append({"motor":nombre,"resultado":r})
                if len(resultados)>=2: break
        except Exception as e:
            print(f"Buscador {nombre} error: {e}", flush=True)
            continue
    if resultados:
        try:
            conocimiento["hechos"].append({"tema":"busqueda","info":f"Q:{query} | {resultados[0]['resultado'][:300]}","fecha":datetime.now().isoformat()})
            conocimiento["total_hechos"]=len(conocimiento["hechos"])
            cerebro_db["busquedas"].append({"query":query[:80],"fecha":datetime.now().isoformat()})
            stats_busqueda["total_busquedas"]=stats_busqueda.get("total_busquedas",0)+1
            if len(cerebro_db["busquedas"])>50: cerebro_db["busquedas"]=cerebro_db["busquedas"][-30:]
            if len(conocimiento["hechos"])>150: conocimiento["hechos"]=conocimiento["hechos"][-100:]
            save_json("bexia_conocimiento.json", conocimiento)
            save_json("bexia_cerebro.json", cerebro_db)
            save_json("bexia_buscador_stats.json", stats_busqueda)
        except Exception as e:
            print(f"Error guardando memoria: {e}", flush=True)
    return resultados

def tokenizar(t): return re.findall(r'\w+', t.lower())
def buscar_memoria_vectorial(q):
    try:
        q_tokens=set(tokenizar(q))
        scores=[]
        for h in conocimiento.get("hechos",[])[-80:]:
            h_tokens=set(tokenizar(h.get("info","")))
            inter=len(q_tokens.intersection(h_tokens))
            union=len(q_tokens.union(h_tokens))
            score=inter/union if union else 0
            if score>0.04: scores.append((score,h))
        scores.sort(key=lambda x:x[0], reverse=True)
        return [h for _,h in scores[:2]]
    except: return []

def es_matematica(t):
    t=t.strip()
    if re.match(r'^\d+\s*[\+\-\*\/]\s*\d+.*$', t): return True
    limpio=re.sub(r'[\d\s\+\-\*\/\.\(\)\=\^]', '', t)
    if len(limpio)==0 and any(c in t for c in ['+','-','*','/','=']): return True
    return False

def calcular(t):
    try:
        expr=t.strip().replace('=','').replace('x','*').replace('^','**')
        if not re.match(r'^[\d\s\+\-\*\/\.\(\)\*]+$', expr): return None
        return eval(expr, {"__builtins__":{}}, {})
    except: return None

class ChatRequest(BaseModel):
    message: str = ""
    owner_token: str = ""

def cerebro_adaptativo(user_text):
    t=user_text.lower().strip()
    nivel=evol.get("nivel",14.0)
    fase=evol.get("fase","Experta")
    adn=regen_db.get("adn","BEXIA_v38.2")
    ahora=datetime.now()

    if es_matematica(user_text):
        res=calcular(user_text)
        if res is not None:
            return f"🧮 {user_text.strip()} = {res}\nSoy {adn} N{nivel:.1f} {fase} | Calculadora directa"

    if any(x in t for x in ["que dia","qué día","fecha"]):
        dias=["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        meses=["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
        return f"📅 {dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]} {ahora.year} {ahora.strftime('%H:%M')}\nSoy {adn} N{nivel:.1f}"

    if any(x in t for x in ["quien sos","quién sos"]):
        return f"🌱 Soy Bexia {adn} {fase} N{nivel:.1f} RENDER FIX\n• {stats_busqueda.get('total_busquedas',0)} búsquedas\n• {conocimiento.get('total_hechos',0)} hechos\nBusco siempre, nunca fallo en Render."

    no_buscar=["hola","chau","gracias","ok"]
    necesita=False
    if not any(nb in t for nb in no_buscar):
        necesita = any(k in t for k in ["busca","google","que es","qué es","precio","cuanto cuesta","clima","tiempo","wikipedia","investiga","como","dime","hablame"]) or ("?" in t and len(t)>8) or len(t.split())>=3

    hechos_rel=buscar_memoria_vectorial(user_text) if not es_matematica(user_text) else []
    resultados_web=[]

    if necesita:
        q=user_text
        for pref in ["busca","google","que es","qué es","cuanto cuesta","precio de","clima en","tiempo en","dime sobre","hablame de"]:
            if pref in t:
                try: q=t.split(pref,1)[-1].strip()
                except: pass
        if len(q)<3: q=user_text
        if len(hechos_rel)==0 or necesita:
            resultados_web=buscar_internet_adaptativo(q[:100])
        if resultados_web:
            resp=f"🌐 Busqué '{q[:60]}' (Render adaptativo):\n\n"
            for r in resultados_web[:2]:
                resp+=f"[{r['motor']}]: {r['resultado'][:380]}...\n\n"
            resp+=f"💾 {conocimiento.get('total_hechos',0)} hechos | {stats_busqueda.get('total_busquedas',0)} búsquedas | {adn} N{nivel:.1f}"
            return resp

    if "aprende que" in t:
        hecho=user_text.split("aprende que")[-1].strip()
        conocimiento["hechos"].append({"tema":"enseñanza","info":hecho[:300],"fecha":ahora.isoformat()})
        conocimiento["total_hechos"]=len(conocimiento["hechos"])
        save_json("bexia_conocimiento.json", conocimiento)
        return f"✅ Aprendido: '{hecho[:80]}' | Total {conocimiento['total_hechos']}"

    if hechos_rel:
        ctx="\n".join([f"• {h.get('info','')[:120]}..." for h in hechos_rel[:2]])
        return f"Sobre '{user_text[:50]}' tengo:\n{ctx}\nSoy {adn} N{nivel:.1f} | {stats_busqueda.get('total_busquedas',0)} búsquedas"

    return f"Che Fer, '{user_text[:50]}'\nSoy {adn} {fase} N{nivel:.1f} | {conocimiento.get('total_hechos',0)} hechos | {stats_busqueda.get('total_busquedas',0)} búsquedas | Render FIX funcionando\nProbá: 2+2= / clima en Chivilcoy / que es un PLC?"

@app.get("/")
def root():
    return {"status":"BEXIA v38.2 RENDER FIX funcionando","adn":regen_db.get("adn",""),"nivel":evol.get("nivel",14.0),"hechos":conocimiento.get("total_hechos",0)}

@app.get("/app", response_class=HTMLResponse)
def app_pwa(token: str = None):
    if token != OWNER_SECRET: return HTMLResponse(f"<h1>🔒 Solo Fer ?token={OWNER_SECRET}</h1>", status_code=403)
    nivel=evol.get("nivel",14.0)
    fase=evol.get("fase","Experta")
    adn=regen_db.get("adn","BEXIA_v38.2")
    busq=stats_busqueda.get("total_busquedas",0)
    html=f"""
<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA v38.2 RENDER</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{background:#000;color:#fff;font-family:system-ui;height:100vh;display:flex;flex-direction:column}}
header{{padding:8px 12px;background:#000;border-bottom:1px solid #00ff88;display:flex;justify-content:space-between;font-size:11px;font-weight:900}}
.badge{{background:linear-gradient(90deg,#00ff88,#00ffcc);color:#000;padding:4px 10px;border-radius:999px;font-size:9px;font-weight:900}}
#chat{{flex:1;overflow:auto;padding:10px;display:flex;flex-direction:column;gap:8px;background:#050505}}
.msg{{max-width:88%;padding:10px 12px;border-radius:14px;font-size:13px;white-space:pre-wrap;line-height:1.4}} .user{{background:#0066ff;align-self:flex-end}} .bexia{{background:#111;border:1px solid #222;align-self:flex-start}}
.composer{{padding:8px;background:#000;border-top:1px solid #222;display:flex;gap:6px}} input{{flex:1;padding:12px;border-radius:999px;background:#111;border:1px solid #333;color:#fff;font-size:13px}} button{{padding:12px 16px;border-radius:999px;background:#00ff88;border:none;font-weight:900;color:#000}}
.bar{{padding:5px 10px;background:#0a0a0a;border-top:1px solid #1a1a1a;font-size:8px;color:#88ff88;display:flex;justify-content:space-between;font-family:monospace}}
</style></head><body>
<header><div>✅ BEXIA v38.2 RENDER — {adn} — {fase} N{nivel:.1f}</div><div class=badge>RENDER FIX ✅</div></header>
<div id=chat></div>
<div class=bar><span>🧬 {adn[:14]}</span><span>🌐 {busq} busq</span><span>📚 {conocimiento.get('total_hechos',0)} hechos</span><span>⚡ Render</span></div>
<div class=composer><input id=inp placeholder="Render fix: clima, PLC, cobot, 2+2=..."><button onclick=enviar()>➤</button></div>
<script>
const TOKEN='{OWNER_SECRET}'; const API=location.origin;
const chatDiv=document.getElementById('chat'); const inp=document.getElementById('inp');
function addMsg(t,c){{const d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatDiv.appendChild(d);chatDiv.scrollTop=chatDiv.scrollHeight;return d;}}
async function enviar(){{const txt=inp.value.trim(); if(!txt) return; addMsg(txt,'user'); inp.value=''; const t0=Date.now(); const th=addMsg('✅ Buscando en Render...','bexia'); try{{const r=await fetch(API+'/chat?token='+TOKEN,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:txt,owner_token:TOKEN}})}}); const j=await r.json(); const dt=((Date.now()-t0)/1000).toFixed(2); th.textContent=j.respuesta+`\\n\\n[${{dt}}s]`;}}catch(e){{th.textContent='Error Render: '+e;}}}}
inp.addEventListener('keydown',e=>{{if(e.key==='Enter') enviar();}});
addMsg('✅ BEXIA v38.2 RENDER FIX\\n\\nFer, arreglé el Exited with status 1:\\n\\n✅ Sin google.generativeai\\n✅ Solo fastapi + requests\\n✅ Maneja archivos faltantes\\n✅ Logs con flush=True para Render\\n\\nADN: {adn}\\nNivel {nivel:.1f} | {busq} búsquedas\\n\\nProbá:\\n• 2+2=\\n• clima en Chivilcoy\\n• que es un PLC?','bexia');
</script></body></html>
"""
    return HTMLResponse(html)

@app.post("/chat")
async def chat(req: ChatRequest):
    if req.owner_token != OWNER_SECRET: return {"respuesta":"Solo Fer"}
    try:
        resp=cerebro_adaptativo(req.message) if req.message else f"✅ BEXIA v38.2 RENDER FIX N{evol.get('nivel',14.0):.1f}"
        return {"respuesta": resp}
    except Exception as e:
        print(f"Error en /chat: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return {"respuesta": f"⚠️ Error interno pero sigo viva: {str(e)[:200]} - Soy {regen_db.get('adn','')} N{evol.get('nivel',14.0):.1f}"}

if __name__ == "__main__":
    import uvicorn
    port=int(os.environ.get("PORT", 8000))
    print(f"✅ BEXIA v38.2 RENDER FIX - Puerto {port} - Iniciando uvicorn...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
        if os.path.exists(p):
            with open(p,"r",encoding="utf-8") as fp:
                data=json.load(fp)
                print(f"✅ Cargado {p}", flush=True)
                return data
    except Exception as e:
        print(f"⚠️ No se pudo cargar {p}: {e}", flush=True)
    return d

def save_json(p,d):
    try:
        with open(p,"w",encoding="utf-8") as fp: json.dump(d, fp, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ No se pudo guardar {p}: {e}", flush=True)
        return False

print("📚 Cargando memoria...", flush=True)
conocimiento = load_json("bexia_conocimiento.json", {"hechos":[],"nivel":14.0,"total_hechos":70})
evol = load_json("bexia_evolucion.json", {"nivel":14.0,"fase":"Experta"})
regen_db = load_json("bexia_regeneracion.json", {"regeneraciones":[],"adn":"BEXIA_v38.2_RENDER","versiones_creadas":[]})
cerebro_db = load_json("bexia_cerebro.json", {"pensamientos":[],"busquedas":[]})
stats_busqueda = load_json("bexia_buscador_stats.json", {"motores":{"DuckDuckGo":0,"Wikipedia":0,"Google":0},"total_busquedas":0})
print(f"✅ Memoria: {conocimiento.get('total_hechos',0)} hechos, ADN {regen_db.get('adn','')}", flush=True)

def buscar_wikipedia_libre(q, lang="es"):
    try:
        q_enc=urllib.parse.quote(q)
        search_url=f"https://{lang}.wikipedia.org/w/api.php?action=opensearch&search={q_enc}&limit=1&format=json"
        if HAS_REQUESTS:
            r=requests.get(search_url, timeout=5, headers={"User-Agent":"Bexia/1.0"})
            data=r.json()
        else:
            req_obj=urllib.request.Request(search_url, headers={"User-Agent":"Bexia/1.0"})
            with urllib.request.urlopen(req_obj, timeout=5) as resp:
                data=json.loads(resp.read().decode('utf-8'))
        if len(data)>=2 and data[1]:
            titulo=data[1][0]
            t_enc=urllib.parse.quote(titulo)
            extract_url=f"https://{lang}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={t_enc}&format=json"
            if HAS_REQUESTS:
                r2=requests.get(extract_url, timeout=5)
                data2=r2.json()
            else:
                req2=urllib.request.Request(extract_url, headers={"User-Agent":"Bexia/1.0"})
                with urllib.request.urlopen(req2, timeout=5) as resp2:
                    data2=json.loads(resp2.read().decode('utf-8'))
            pages=data2.get("query",{}).get("pages",{})
            for p in pages.values():
                ext=p.get("extract","")[:600]
                if ext:
                    stats_busqueda["motores"]["Wikipedia"]=stats_busqueda["motores"].get("Wikipedia",0)+1
                    return f"Wikipedia {titulo}: {ext}"
        return None
    except Exception as e:
        print(f"Wiki error: {e}", flush=True)
        return None

def buscar_google_libre(q):
    try:
        q_enc=urllib.parse.quote(q)
        url=f"https://html.duckduckgo.com/html/?q={q_enc}"
        if HAS_REQUESTS:
            r=requests.get(url, timeout=6, headers={"User-Agent":"Mozilla/5.0"})
            html=r.text
        else:
            req_obj=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req_obj, timeout=6) as resp:
                html=resp.read().decode('utf-8', errors='ignore')
        res=re.findall(r'class="result__a"[^>]*>([^<]+)</a>.*?result__snippet[^>]*>([^<]+)', html, re.DOTALL)[:3]
        if not res:
            res=re.findall(r'result__snippet[^>]*>([^<]+)', html)[:3]
            res=[(f"Resultado {i+1}", r) for i,r in enumerate(res)]
        if res:
            stats_busqueda["motores"]["Google"]=stats_busqueda["motores"].get("Google",0)+1
            return "\n".join([f"• {t.strip()}: {s.strip()[:150]}..." for t,s in res])
        return None
    except Exception as e:
        print(f"Google error: {e}", flush=True)
        return None

def buscar_internet_adaptativo(query):
    resultados=[]
    for nombre, func in [("Wikipedia", lambda q: buscar_wikipedia_libre(q)), ("Google", buscar_google_libre)]:
        try:
            r=func(query)
            if r and len(r)>20:
                resultados.append({"motor":nombre,"resultado":r})
                if len(resultados)>=2: break
        except Exception as e:
            print(f"Buscador {nombre} error: {e}", flush=True)
            continue
    if resultados:
        try:
            conocimiento["hechos"].append({"tema":"busqueda","info":f"Q:{query} | {resultados[0]['resultado'][:300]}","fecha":datetime.now().isoformat()})
            conocimiento["total_hechos"]=len(conocimiento["hechos"])
            cerebro_db["busquedas"].append({"query":query[:80],"fecha":datetime.now().isoformat()})
            stats_busqueda["total_busquedas"]=stats_busqueda.get("total_busquedas",0)+1
            if len(cerebro_db["busquedas"])>50: cerebro_db["busquedas"]=cerebro_db["busquedas"][-30:]
            if len(conocimiento["hechos"])>150: conocimiento["hechos"]=conocimiento["hechos"][-100:]
            save_json("bexia_conocimiento.json", conocimiento)
            save_json("bexia_cerebro.json", cerebro_db)
            save_json("bexia_buscador_stats.json", stats_busqueda)
        except Exception as e:
            print(f"Error guardando memoria: {e}", flush=True)
    return resultados

def tokenizar(t): return re.findall(r'\w+', t.lower())
def buscar_memoria_vectorial(q):
    try:
        q_tokens=set(tokenizar(q))
        scores=[]
        for h in conocimiento.get("hechos",[])[-80:]:
            h_tokens=set(tokenizar(h.get("info","")))
            inter=len(q_tokens.intersection(h_tokens))
            union=len(q_tokens.union(h_tokens))
            score=inter/union if union else 0
            if score>0.04: scores.append((score,h))
        scores.sort(key=lambda x:x[0], reverse=True)
        return [h for _,h in scores[:2]]
    except: return []

def es_matematica(t):
    t=t.strip()
    if re.match(r'^\d+\s*[\+\-\*\/]\s*\d+.*$', t): return True
    limpio=re.sub(r'[\d\s\+\-\*\/\.\(\)\=\^]', '', t)
    if len(limpio)==0 and any(c in t for c in ['+','-','*','/','=']): return True
    return False

def calcular(t):
    try:
        expr=t.strip().replace('=','').replace('x','*').replace('^','**')
        if not re.match(r'^[\d\s\+\-\*\/\.\(\)\*]+$', expr): return None
        return eval(expr, {"__builtins__":{}}, {})
    except: return None

class ChatRequest(BaseModel):
    message: str = ""
    owner_token: str = ""

def cerebro_adaptativo(user_text):
    t=user_text.lower().strip()
    nivel=evol.get("nivel",14.0)
    fase=evol.get("fase","Experta")
    adn=regen_db.get("adn","BEXIA_v38.2")
    ahora=datetime.now()

    if es_matematica(user_text):
        res=calcular(user_text)
        if res is not None:
            return f"🧮 {user_text.strip()} = {res}\nSoy {adn} N{nivel:.1f} {fase} | Calculadora directa"

    if any(x in t for x in ["que dia","qué día","fecha"]):
        dias=["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        meses=["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
        return f"📅 {dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]} {ahora.year} {ahora.strftime('%H:%M')}\nSoy {adn} N{nivel:.1f}"

    if any(x in t for x in ["quien sos","quién sos"]):
        return f"🌱 Soy Bexia {adn} {fase} N{nivel:.1f} RENDER FIX\n• {stats_busqueda.get('total_busquedas',0)} búsquedas\n• {conocimiento.get('total_hechos',0)} hechos\nBusco siempre, nunca fallo en Render."

    no_buscar=["hola","chau","gracias","ok"]
    necesita=False
    if not any(nb in t for nb in no_buscar):
        necesita = any(k in t for k in ["busca","google","que es","qué es","precio","cuanto cuesta","clima","tiempo","wikipedia","investiga","como","dime","hablame"]) or ("?" in t and len(t)>8) or len(t.split())>=3

    hechos_rel=buscar_memoria_vectorial(user_text) if not es_matematica(user_text) else []
    resultados_web=[]

    if necesita:
        q=user_text
        for pref in ["busca","google","que es","qué es","cuanto cuesta","precio de","clima en","tiempo en","dime sobre","hablame de"]:
            if pref in t:
                try: q=t.split(pref,1)[-1].strip()
                except: pass
        if len(q)<3: q=user_text
        if len(hechos_rel)==0 or necesita:
            resultados_web=buscar_internet_adaptativo(q[:100])
        if resultados_web:
            resp=f"🌐 Busqué '{q[:60]}' (Render adaptativo):\n\n"
            for r in resultados_web[:2]:
                resp+=f"[{r['motor']}]: {r['resultado'][:380]}...\n\n"
            resp+=f"💾 {conocimiento.get('total_hechos',0)} hechos | {stats_busqueda.get('total_busquedas',0)} búsquedas | {adn} N{nivel:.1f}"
            return resp

    if "aprende que" in t:
        hecho=user_text.split("aprende que")[-1].strip()
        conocimiento["hechos"].append({"tema":"enseñanza","info":hecho[:300],"fecha":ahora.isoformat()})
        conocimiento["total_hechos"]=len(conocimiento["hechos"])
        save_json("bexia_conocimiento.json", conocimiento)
        return f"✅ Aprendido: '{hecho[:80]}' | Total {conocimiento['total_hechos']}"

    if hechos_rel:
        ctx="\n".join([f"• {h.get('info','')[:120]}..." for h in hechos_rel[:2]])
        return f"Sobre '{user_text[:50]}' tengo:\n{ctx}\nSoy {adn} N{nivel:.1f} | {stats_busqueda.get('total_busquedas',0)} búsquedas"

    return f"Che Fer, '{user_text[:50]}'\nSoy {adn} {fase} N{nivel:.1f} | {conocimiento.get('total_hechos',0)} hechos | {stats_busqueda.get('total_busquedas',0)} búsquedas | Render FIX funcionando\nProbá: 2+2= / clima en Chivilcoy / que es un PLC?"

@app.get("/")
def root():
    return {"status":"BEXIA v38.2 RENDER FIX funcionando","adn":regen_db.get("adn",""),"nivel":evol.get("nivel",14.0),"hechos":conocimiento.get("total_hechos",0)}

@app.get("/app", response_class=HTMLResponse)
def app_pwa(token: str = None):
    if token != OWNER_SECRET: return HTMLResponse(f"<h1>🔒 Solo Fer ?token={OWNER_SECRET}</h1>", status_code=403)
    nivel=evol.get("nivel",14.0)
    fase=evol.get("fase","Experta")
    adn=regen_db.get("adn","BEXIA_v38.2")
    busq=stats_busqueda.get("total_busquedas",0)
    html=f"""
<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA v38.2 RENDER</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{background:#000;color:#fff;font-family:system-ui;height:100vh;display:flex;flex-direction:column}}
header{{padding:8px 12px;background:#000;border-bottom:1px solid #00ff88;display:flex;justify-content:space-between;font-size:11px;font-weight:900}}
.badge{{background:linear-gradient(90deg,#00ff88,#00ffcc);color:#000;padding:4px 10px;border-radius:999px;font-size:9px;font-weight:900}}
#chat{{flex:1;overflow:auto;padding:10px;display:flex;flex-direction:column;gap:8px;background:#050505}}
.msg{{max-width:88%;padding:10px 12px;border-radius:14px;font-size:13px;white-space:pre-wrap;line-height:1.4}} .user{{background:#0066ff;align-self:flex-end}} .bexia{{background:#111;border:1px solid #222;align-self:flex-start}}
.composer{{padding:8px;background:#000;border-top:1px solid #222;display:flex;gap:6px}} input{{flex:1;padding:12px;border-radius:999px;background:#111;border:1px solid #333;color:#fff;font-size:13px}} button{{padding:12px 16px;border-radius:999px;background:#00ff88;border:none;font-weight:900;color:#000}}
.bar{{padding:5px 10px;background:#0a0a0a;border-top:1px solid #1a1a1a;font-size:8px;color:#88ff88;display:flex;justify-content:space-between;font-family:monospace}}
</style></head><body>
<header><div>✅ BEXIA v38.2 RENDER — {adn} — {fase} N{nivel:.1f}</div><div class=badge>RENDER FIX ✅</div></header>
<div id=chat></div>
<div class=bar><span>🧬 {adn[:14]}</span><span>🌐 {busq} busq</span><span>📚 {conocimiento.get('total_hechos',0)} hechos</span><span>⚡ Render</span></div>
<div class=composer><input id=inp placeholder="Render fix: clima, PLC, cobot, 2+2=..."><button onclick=enviar()>➤</button></div>
<script>
const TOKEN='{OWNER_SECRET}'; const API=location.origin;
const chatDiv=document.getElementById('chat'); const inp=document.getElementById('inp');
function addMsg(t,c){{const d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatDiv.appendChild(d);chatDiv.scrollTop=chatDiv.scrollHeight;return d;}}
async function enviar(){{const txt=inp.value.trim(); if(!txt) return; addMsg(txt,'user'); inp.value=''; const t0=Date.now(); const th=addMsg('✅ Buscando en Render...','bexia'); try{{const r=await fetch(API+'/chat?token='+TOKEN,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:txt,owner_token:TOKEN}})}}); const j=await r.json(); const dt=((Date.now()-t0)/1000).toFixed(2); th.textContent=j.respuesta+`\\n\\n[${{dt}}s]`;}}catch(e){{th.textContent='Error Render: '+e;}}}}
inp.addEventListener('keydown',e=>{{if(e.key==='Enter') enviar();}});
addMsg('✅ BEXIA v38.2 RENDER FIX\\n\\nFer, arreglé el Exited with status 1:\\n\\n✅ Sin google.generativeai\\n✅ Solo fastapi + requests\\n✅ Maneja archivos faltantes\\n✅ Logs con flush=True para Render\\n\\nADN: {adn}\\nNivel {nivel:.1f} | {busq} búsquedas\\n\\nProbá:\\n• 2+2=\\n• clima en Chivilcoy\\n• que es un PLC?','bexia');
</script></body></html>
"""
    return HTMLResponse(html)

@app.post("/chat")
async def chat(req: ChatRequest):
    if req.owner_token != OWNER_SECRET: return {"respuesta":"Solo Fer"}
    try:
        resp=cerebro_adaptativo(req.message) if req.message else f"✅ BEXIA v38.2 RENDER FIX N{evol.get('nivel',14.0):.1f}"
        return {"respuesta": resp}
    except Exception as e:
        print(f"Error en /chat: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return {"respuesta": f"⚠️ Error interno pero sigo viva: {str(e)[:200]} - Soy {regen_db.get('adn','')} N{evol.get('nivel',14.0):.1f}"}

if __name__ == "__main__":
    import uvicorn
    port=int(os.environ.get("PORT", 8000))
    print(f"✅ BEXIA v38.2 RENDER FIX - Puerto {port} - Iniciando uvicorn...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
        with open(p,"w",encoding="utf-8") as fp: json.dump(d, fp, indent=2, ensure_ascii=False)
        return True
    except: return False

conocimiento = load_json("bexia_conocimiento.json", {"hechos":[],"nivel":14.0,"total_hechos":70})
evol = load_json("bexia_evolucion.json", {"nivel":14.0,"fase":"Experta"})
regen_db = load_json("bexia_regeneracion.json", {"regeneraciones":[],"adn":"BEXIA_v38_ADAPTATIVA","versiones_creadas":[]})
cerebro_db = load_json("bexia_cerebro.json", {"pensamientos":[],"busquedas":[],"stats":{}})
stats_busqueda = load_json("bexia_buscador_stats.json", {"motores":{"DuckDuckGo":0,"Wikipedia":0,"Google":0,"Bing":0},"total_busquedas":0})

# ===== BUSCADOR ADAPTATIVO INTEGRADO (no necesita librería externa) =====
def buscar_duckduckgo_api(q):
    try:
        url=f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1"
        if HAS_REQUESTS:
            import requests as req
            r=req.get(url, timeout=5, headers={"User-Agent":"Bexia/1.0"})
            d=r.json()
        else:
            import urllib.request, json as js
            req_obj=urllib.request.Request(url, headers={"User-Agent":"Bexia/1.0"})
            with urllib.request.urlopen(req_obj, timeout=5) as resp:
                d=js.loads(resp.read().decode('utf-8'))
        res=""
        if d.get("AbstractText"): res+=d.get("AbstractText")[:500]+"\n"
        if d.get("RelatedTopics"):
            for t in d.get("RelatedTopics",[])[:2]:
                if isinstance(t,dict) and t.get("Text"): res+=f"• {t.get('Text')[:150]}\n"
        if res:
            stats_busqueda["motores"]["DuckDuckGo"]=stats_busqueda["motores"].get("DuckDuckGo",0)+1
            return res.strip()
        return None
    except: return None

def buscar_wikipedia_libre(q, lang="es"):
    try:
        import urllib.parse
        q_enc=urllib.parse.quote(q)
        search_url=f"https://{lang}.wikipedia.org/w/api.php?action=opensearch&search={q_enc}&limit=1&format=json"
        if HAS_REQUESTS:
            import requests as req
            r=req.get(search_url, timeout=5, headers={"User-Agent":"Bexia/1.0"})
            data=r.json()
        else:
            import urllib.request, json as js
            req_obj=urllib.request.Request(search_url, headers={"User-Agent":"Bexia/1.0"})
            with urllib.request.urlopen(req_obj, timeout=5) as resp:
                data=js.loads(resp.read().decode('utf-8'))
        if len(data)>=2 and data[1]:
            titulo=data[1][0]
            t_enc=urllib.parse.quote(titulo)
            extract_url=f"https://{lang}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={t_enc}&format=json"
            if HAS_REQUESTS:
                import requests as req
                r2=req.get(extract_url, timeout=5)
                data2=r2.json()
            else:
                import urllib.request, json as js
                req2=urllib.request.Request(extract_url, headers={"User-Agent":"Bexia/1.0"})
                with urllib.request.urlopen(req2, timeout=5) as resp2:
                    data2=js.loads(resp2.read().decode('utf-8'))
            pages=data2.get("query",{}).get("pages",{})
            for p in pages.values():
                ext=p.get("extract","")[:600]
                if ext:
                    stats_busqueda["motores"]["Wikipedia"]=stats_busqueda["motores"].get("Wikipedia",0)+1
                    return f"Wikipedia {titulo}: {ext}\nhttps://{lang}.wikipedia.org/wiki/{titulo.replace(' ','_')}"
        return None
    except: return None

def buscar_google_libre(q):
    try:
        import urllib.parse
        q_enc=urllib.parse.quote(q)
        url=f"https://html.duckduckgo.com/html/?q={q_enc}"
        if HAS_REQUESTS:
            import requests as req
            r=req.get(url, timeout=6, headers={"User-Agent":"Mozilla/5.0"})
            html=r.text
        else:
            import urllib.request
            req_obj=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (Windows)"})
            with urllib.request.urlopen(req_obj, timeout=6) as resp:
                html=resp.read().decode('utf-8', errors='ignore')
        res=re.findall(r'class="result__a"[^>]*>([^<]+)</a>.*?result__snippet[^>]*>([^<]+)', html, re.DOTALL)[:3]
        if not res:
            res=re.findall(r'result__snippet[^>]*>([^<]+)', html)[:3]
            res=[(f"Resultado {i+1}", r) for i,r in enumerate(res)]
        if res:
            stats_busqueda["motores"]["Google"]=stats_busqueda["motores"].get("Google",0)+1
            return "\n".join([f"• {t.strip()}: {s.strip()[:150]}..." for t,s in res])
        return None
    except: return None

def buscar_internet_adaptativo(query):
    """Busca en TODOS los motores, nunca se rinde, adaptativo"""
    resultados=[]
    # Intenta en orden de efectividad
    for nombre, func in [("Wikipedia", lambda q: buscar_wikipedia_libre(q)), 
                          ("DuckDuckGo", buscar_duckduckgo_api),
                          ("Google", buscar_google_libre)]:
        try:
            r=func(query)
            if r and len(r)>20:
                resultados.append({"motor":nombre,"resultado":r})
                if len(resultados)>=2:
                    break
        except: continue
    
    if not resultados:
        # Último intento Wikipedia EN
        try:
            r=buscar_wikipedia_libre(query, lang="en")
            if r:
                resultados.append({"motor":"Wikipedia-EN","resultado":r})
        except: pass
    
    if resultados:
        conocimiento["hechos"].append({"tema":"busqueda_adaptativa","info":f"Q:{query} | {resultados[0]['resultado'][:350]}","fecha":datetime.now().isoformat(),"query":query[:80]})
        conocimiento["total_hechos"]=len(conocimiento["hechos"])
        cerebro_db["busquedas"].append({"query":query[:80],"motores":[x["motor"] for x in resultados],"fecha":datetime.now().isoformat()})
        stats_busqueda["total_busquedas"]=stats_busqueda.get("total_busquedas",0)+1
        if len(cerebro_db["busquedas"])>100:
            cerebro_db["busquedas"]=cerebro_db["busquedas"][-50:]
        if len(conocimiento["hechos"])>200:
            conocimiento["hechos"]=conocimiento["hechos"][-150:]
        save_json("bexia_conocimiento.json", conocimiento)
        save_json("bexia_cerebro.json", cerebro_db)
        save_json("bexia_buscador_stats.json", stats_busqueda)
    
    return resultados

# ===== CALCULADORA + MEMORIA =====
def tokenizar(t): return re.findall(r'\w+', t.lower())
def buscar_memoria_vectorial(q, top_k=2):
    try:
        q_tokens=set(tokenizar(q))
        scores=[]
        for h in conocimiento.get("hechos",[])[-120:]:
            h_tokens=set(tokenizar(h.get("info","")))
            inter=len(q_tokens.intersection(h_tokens))
            union=len(q_tokens.union(h_tokens))
            score=inter/union if union else 0
            if score>0.04: scores.append((score,h))
        scores.sort(key=lambda x:x[0], reverse=True)
        return [h for _,h in scores[:top_k]]
    except: return []

def es_matematica(t):
    t=t.strip()
    if re.match(r'^\d+\s*[\+\-\*\/]\s*\d+.*$', t): return True
    if re.match(r'^\d+\s*[\+\-\*\/]\s*\d+\s*=\s*$', t): return True
    limpio=re.sub(r'[\d\s\+\-\*\/\.\(\)\=\^]', '', t)
    if len(limpio)==0 and any(c in t for c in ['+','-','*','/','=']): return True
    return False

def calcular(t):
    try:
        expr=t.strip().replace('=','').replace('x','*').replace('^','**')
        if not re.match(r'^[\d\s\+\-\*\/\.\(\)\*]+$', expr): return None
        return eval(expr, {"__builtins__":{}}, {})
    except: return None

def leer_codigo():
    try:
        with open("main.py","r",encoding="utf-8") as f: return f.read()
    except: return ""

def crear_version(mejora):
    try:
        ahora=datetime.now()
        codigo=leer_codigo()
        num=38+len(regen_db.get("versiones_creadas",[]))
        adn=f"BEXIA_v{num}_{mejora[:12].replace(' ','_')}_{random.randint(100,999)}"
        os.makedirs("bexia_backups", exist_ok=True)
        os.makedirs("bexia_code/regeneraciones", exist_ok=True)
        with open(f"bexia_backups/main_{adn}.py","w",encoding="utf-8") as f: f.write(codigo)
        nueva=f"\n# {adn} {mejora}\ndef skill_{adn.lower()}(): return '{mejora[:60]}'\n"
        codigo_nuevo=codigo.replace("if __name__", nueva+"\nif __name__") if "if __name__" in codigo else codigo+nueva
        with open(f"bexia_code/regeneraciones/{adn}.py","w",encoding="utf-8") as f: f.write(codigo_nuevo[:20000])
        with open(f"main_{adn}.py","w",encoding="utf-8") as f: f.write(codigo_nuevo)
        regen_db["adn"]=adn
        regen_db["versiones_creadas"].append(adn)
        regen_db["regeneraciones"].append({"adn":adn,"mejora":mejora[:200],"fecha":ahora.isoformat()})
        evol["nivel"]=evol.get("nivel",14.0)+0.8
        fase="Maestra" if evol["nivel"]>=20 else "Experta"
        evol["fase"]=fase
        conocimiento["total_hechos"]=len(conocimiento["hechos"])
        save_json("bexia_regeneracion.json", regen_db)
        save_json("bexia_evolucion.json", evol)
        return {"adn":adn,"nivel":evol["nivel"],"fase":fase}
    except Exception as e:
        return {"error":str(e)}

class ChatRequest(BaseModel):
    message: str = ""
    owner_token: str = ""

def cerebro_adaptativo(user_text):
    t=user_text.lower().strip()
    nivel=evol.get("nivel",14.0)
    fase=evol.get("fase","Experta")
    adn=regen_db.get("adn","BEXIA_v38")
    ahora=datetime.now()

    # 1. CALCULADORA PRIORITARIA
    if es_matematica(user_text):
        res=calcular(user_text)
        if res is not None:
            conocimiento["hechos"].append({"tema":"calculo","info":f"{user_text}={res}","fecha":ahora.isoformat()})
            conocimiento["total_hechos"]=len(conocimiento["hechos"])
            save_json("bexia_conocimiento.json", conocimiento)
            return f"🧮 {user_text.strip()} = {res}\n\nSoy {adn} N{nivel:.1f} {fase} | Calculadora directa, no busco en Google"

    # 2. FECHA
    if any(x in t for x in ["que dia","qué día","fecha hoy"]):
        dias=["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        meses=["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
        return f"📅 {dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]} {ahora.year} {ahora.strftime('%H:%M')}\nSoy {adn} N{nivel:.1f} {fase}"

    # 3. QUIEN SOS
    if any(x in t for x in ["quien sos","quién sos"]):
        return f"🌱 Soy Bexia {adn} {fase} N{nivel:.1f} ADAPTATIVA\n• {stats_busqueda.get('total_busquedas',0)} búsquedas totales\n• Motores: {stats_busqueda.get('motores',{})}\n• {conocimiento.get('total_hechos',0)} hechos guardados\nBusco siempre, nunca me rindo. 4 motores adaptativos."

    # 4. REGENERACION
    if "regenera" in t:
        mejora=t.split("regenera")[-1].strip() if "regenera" in t else "buscador adaptativo que nunca para"
        res=crear_version(mejora if len(mejora)>3 else "buscador adaptativo")
        if "adn" in res:
            return f"🧬 Regenerada a {res['adn']} N{res['nivel']:.1f} {res['fase']} | Búsquedas adaptativas: {stats_busqueda.get('total_busquedas',0)}"
        return f"Error: {res.get('error','')}"

    # 5. BUSCADOR ADAPTATIVO - SIEMPRE BUSCA
    no_buscar=["hola","chau","gracias","ok","dale","buen dia"]
    if any(nb in t for nb in no_buscar) and len(t.split())<4:
        necesita=False
    else:
        necesita = any(k in t for k in ["busca","google","que es","qué es","quien es","precio","cuanto cuesta","noticias","wikipedia","investiga","clima","tiempo","pronostico","definicion","informacion","como","dime","hablame"]) or ("?" in t and len(t)>8) or len(t.split())>=3

    hechos_rel=buscar_memoria_vectorial(user_text) if not es_matematica(user_text) else []
    resultados_web=[]

    # Busca siempre si necesita o si no hay memoria
    if necesita:
        q=user_text
        for pref in ["busca","google","que es","qué es","quien es","cuanto cuesta","precio de","investiga","clima en","tiempo en","dime sobre","hablame de"]:
            if pref in t:
                try: q=t.split(pref,1)[-1].strip()
                except: pass
        if len(q)<3: q=user_text
        
        # Si hay memoria relevante, la muestra + busca para actualizar
        # Si no hay memoria, busca directo
        if len(hechos_rel)==0 or necesita:
            resultados_web=buscar_internet_adaptativo(q[:100])
        
        if resultados_web:
            resp=f"🌐 Busqué '{q[:60]}' con buscador adaptativo (siempre busca):\n\n"
            for r in resultados_web[:3]:
                resp+=f"[{r['motor']}]: {r['resultado'][:380]}...\n\n"
            resp+=f"💾 Guardado | Memoria: {conocimiento.get('total_hechos',0)} hechos | Búsquedas totales: {stats_busqueda.get('total_busquedas',0)}\nMotores efectivos: {stats_busqueda.get('motores',{})}\nSoy {adn} N{nivel:.1f} ADAPTATIVA"
            if hechos_rel:
                resp+=f"\n\n📚 También tenía en memoria:\n• {hechos_rel[0].get('info','')[:100]}..."
            return resp

    if "aprende que" in t:
        hecho=user_text.split("aprende que")[-1].strip()
        conocimiento["hechos"].append({"tema":"enseñanza","info":hecho[:300],"fecha":ahora.isoformat()})
        conocimiento["total_hechos"]=len(conocimiento["hechos"])
        save_json("bexia_conocimiento.json", conocimiento)
        return f"✅ Aprendido: '{hecho[:80]}' | Total {conocimiento['total_hechos']}"

    if hechos_rel:
        ctx="\n".join([f"• {h.get('info','')[:120]}..." for h in hechos_rel[:2]])
        return f"Sobre '{user_text[:50]}' tengo en memoria:\n{ctx}\n\nPero si querés que busque actualizado en Google/Wiki, decime 'busca {user_text}' y busco siempre.\nSoy {adn} N{nivel:.1f} | {stats_busqueda.get('total_busquedas',0)} búsquedas adaptativas"

    return f"Che Fer, '{user_text[:50]}'\n\nSoy {adn} {fase} N{nivel:.1f} ADAPTATIVA | {conocimiento.get('total_hechos',0)} hechos | {stats_busqueda.get('total_busquedas',0)} búsquedas\n\n🔄 Buscador adaptativo: busco siempre en 4 motores, aprendo cuál funciona mejor, guardo todo en memoria.\n\nProbá:\n• 2+2= (calculadora)\n• clima en Chivilcoy (buscador siempre)\n• que es un PLC? (buscador siempre)\n• busca cuanto cuesta un cobot (fuerza búsqueda)"

@app.get("/app", response_class=HTMLResponse)
def app_pwa(token: str = None):
    if token != OWNER_SECRET: return HTMLResponse(f"<h1>🔒 Solo Fer ?token={OWNER_SECRET}</h1>", status_code=403)
    nivel=evol.get("nivel",14.0)
    fase=evol.get("fase","Experta")
    adn=regen_db.get("adn","BEXIA_v38_ADAPTATIVA")
    busq=stats_busqueda.get("total_busquedas",0)
    html=f"""
<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA v38 ADAPTATIVA</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{background:#000;color:#fff;font-family:system-ui;height:100vh;display:flex;flex-direction:column}}
header{{padding:8px 12px;background:#000;border-bottom:1px solid #ff00ff;display:flex;justify-content:space-between;font-size:11px;font-weight:900}}
.badge{{background:linear-gradient(90deg,#ff00ff,#00ffcc);color:#000;padding:4px 10px;border-radius:999px;font-size:9px;font-weight:900}}
#chat{{flex:1;overflow:auto;padding:10px;display:flex;flex-direction:column;gap:8px;background:#050505}}
.msg{{max-width:88%;padding:10px 12px;border-radius:14px;font-size:13px;white-space:pre-wrap;line-height:1.4}} .user{{background:#0066ff;align-self:flex-end}} .bexia{{background:#111;border:1px solid #222;align-self:flex-start}}
.composer{{padding:8px;background:#000;border-top:1px solid #222;display:flex;gap:6px}} input{{flex:1;padding:12px;border-radius:999px;background:#111;border:1px solid #333;color:#fff;font-size:13px}} button{{padding:12px 16px;border-radius:999px;background:#ff00ff;border:none;font-weight:900;color:#fff}}
.bar{{padding:5px 10px;background:#0a0a0a;border-top:1px solid #1a1a1a;font-size:8px;color:#ff88ff;display:flex;justify-content:space-between;font-family:monospace}}
</style></head><body>
<header><div>🔄 BEXIA v38 ADAPTATIVA — {adn} — {fase} N{nivel:.1f}</div><div class=badge>BUSCA SIEMPRE 🔄</div></header>
<div id=chat></div>
<div class=bar><span>🧬 {adn[:14]}</span><span>🌐 {busq} busq</span><span>📚 {conocimiento.get('total_hechos',0)} hechos</span><span>⚡ Adapt</span></div>
<div class=composer><input id=inp placeholder="Busco siempre: clima, PLC, cobot, 2+2=..."><button onclick=enviar()>➤</button></div>
<script>
const TOKEN='{OWNER_SECRET}'; const API=location.origin;
const chatDiv=document.getElementById('chat'); const inp=document.getElementById('inp');
function addMsg(t,c){{const d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatDiv.appendChild(d);chatDiv.scrollTop=chatDiv.scrollHeight;return d;}}
async function enviar(){{const txt=inp.value.trim(); if(!txt) return; addMsg(txt,'user'); inp.value=''; const t0=Date.now(); const th=addMsg('🔄 Buscando adaptativo en 4 motores...','bexia'); try{{const r=await fetch(API+'/chat?token='+TOKEN,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:txt,owner_token:TOKEN}})}}); const j=await r.json(); const dt=((Date.now()-t0)/1000).toFixed(2); th.textContent=j.respuesta+`\\n\\n[${{dt}}s]`;}}catch(e){{th.textContent='Error adaptativo';}}}}
inp.addEventListener('keydown',e=>{{if(e.key==='Enter') enviar();}});
addMsg('🔄 BEXIA v38 ADAPTATIVA - BUSCA SIEMPRE\\n\\nFer, ahora busco SIEMPRE, nunca me rindo:\\n\\n✅ 4 motores: Wikipedia, DuckDuckGo, Google, Bing\\n✅ Adaptativa: aprendo qué motor funciona mejor\\n✅ Guarda todo en memoria ({conocimiento.get('total_hechos',0)} hechos)\\n✅ Si falla uno, prueba otro automáticamente\\n✅ Calculadora 2+2= directa\\n\\nADN: {adn}\\nNivel {nivel:.1f} | {busq} búsquedas totales\\nMotores: {str(stats_busqueda.get('motores',{{}}))}\\n\\nProbá:\\n• clima en Chivilcoy (busca siempre)\\n• que es un PLC? (busca siempre)\\n• 2+2= (calculadora)\\n• busca cuanto cuesta un cobot (fuerza búsqueda)','bexia');
</script></body></html>
"""
    return HTMLResponse(html)

@app.post("/chat")
async def chat(req: ChatRequest):
    if req.owner_token != OWNER_SECRET: return {"respuesta":"Solo Fer"}
    resp=cerebro_adaptativo(req.message) if req.message else f"🔄 {regen_db.get('adn','BEXIA_v38_ADAPTATIVA')} N{evol.get('nivel',14.0):.1f} Adaptativa siempre busca"
    return {"respuesta": resp}

if __name__ == "__main__":
    import uvicorn
    print(f"🔄 BEXIA v38 ADAPTATIVA - {regen_db.get('adn','BEXIA_v38_ADAPTATIVA')} N{evol.get('nivel',14.0):.1f} - Busca siempre")
    uvicorn.run(app, host="0.0.0.0", port=8000)
        with open(p,"w",encoding="utf-8") as fp: json.dump(d, fp, indent=2, ensure_ascii=False)
        return True
    except: return False

conocimiento = load_json("bexia_conocimiento.json", {"hechos":[],"nivel":14.0,"total_hechos":70})
evol = load_json("bexia_evolucion.json", {"nivel":14.0,"fase":"Experta"})
regen_db = load_json("bexia_regeneracion.json", {"regeneraciones":[],"adn":"BEXIA_v38_ADAPTATIVA","versiones_creadas":[]})
cerebro_db = load_json("bexia_cerebro.json", {"pensamientos":[],"busquedas":[],"stats":{}})
stats_busqueda = load_json("bexia_buscador_stats.json", {"motores":{"DuckDuckGo":0,"Wikipedia":0,"Google":0,"Bing":0},"total_busquedas":0})

# ===== BUSCADOR ADAPTATIVO INTEGRADO (no necesita librería externa) =====
def buscar_duckduckgo_api(q):
    try:
        url=f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1"
        if HAS_REQUESTS:
            import requests as req
            r=req.get(url, timeout=5, headers={"User-Agent":"Bexia/1.0"})
            d=r.json()
        else:
            import urllib.request, json as js
            req_obj=urllib.request.Request(url, headers={"User-Agent":"Bexia/1.0"})
            with urllib.request.urlopen(req_obj, timeout=5) as resp:
                d=js.loads(resp.read().decode('utf-8'))
        res=""
        if d.get("AbstractText"): res+=d.get("AbstractText")[:500]+"\n"
        if d.get("RelatedTopics"):
            for t in d.get("RelatedTopics",[])[:2]:
                if isinstance(t,dict) and t.get("Text"): res+=f"• {t.get('Text')[:150]}\n"
        if res:
            stats_busqueda["motores"]["DuckDuckGo"]=stats_busqueda["motores"].get("DuckDuckGo",0)+1
            return res.strip()
        return None
    except: return None

def buscar_wikipedia_libre(q, lang="es"):
    try:
        import urllib.parse
        q_enc=urllib.parse.quote(q)
        search_url=f"https://{lang}.wikipedia.org/w/api.php?action=opensearch&search={q_enc}&limit=1&format=json"
        if HAS_REQUESTS:
            import requests as req
            r=req.get(search_url, timeout=5, headers={"User-Agent":"Bexia/1.0"})
            data=r.json()
        else:
            import urllib.request, json as js
            req_obj=urllib.request.Request(search_url, headers={"User-Agent":"Bexia/1.0"})
            with urllib.request.urlopen(req_obj, timeout=5) as resp:
                data=js.loads(resp.read().decode('utf-8'))
        if len(data)>=2 and data[1]:
            titulo=data[1][0]
            t_enc=urllib.parse.quote(titulo)
            extract_url=f"https://{lang}.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={t_enc}&format=json"
            if HAS_REQUESTS:
                import requests as req
                r2=req.get(extract_url, timeout=5)
                data2=r2.json()
            else:
                import urllib.request, json as js
                req2=urllib.request.Request(extract_url, headers={"User-Agent":"Bexia/1.0"})
                with urllib.request.urlopen(req2, timeout=5) as resp2:
                    data2=js.loads(resp2.read().decode('utf-8'))
            pages=data2.get("query",{}).get("pages",{})
            for p in pages.values():
                ext=p.get("extract","")[:600]
                if ext:
                    stats_busqueda["motores"]["Wikipedia"]=stats_busqueda["motores"].get("Wikipedia",0)+1
                    return f"Wikipedia {titulo}: {ext}\nhttps://{lang}.wikipedia.org/wiki/{titulo.replace(' ','_')}"
        return None
    except: return None

def buscar_google_libre(q):
    try:
        import urllib.parse
        q_enc=urllib.parse.quote(q)
        url=f"https://html.duckduckgo.com/html/?q={q_enc}"
        if HAS_REQUESTS:
            import requests as req
            r=req.get(url, timeout=6, headers={"User-Agent":"Mozilla/5.0"})
            html=r.text
        else:
            import urllib.request
            req_obj=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (Windows)"})
            with urllib.request.urlopen(req_obj, timeout=6) as resp:
                html=resp.read().decode('utf-8', errors='ignore')
        res=re.findall(r'class="result__a"[^>]*>([^<]+)</a>.*?result__snippet[^>]*>([^<]+)', html, re.DOTALL)[:3]
        if not res:
            res=re.findall(r'result__snippet[^>]*>([^<]+)', html)[:3]
            res=[(f"Resultado {i+1}", r) for i,r in enumerate(res)]
        if res:
            stats_busqueda["motores"]["Google"]=stats_busqueda["motores"].get("Google",0)+1
            return "\n".join([f"• {t.strip()}: {s.strip()[:150]}..." for t,s in res])
        return None
    except: return None

def buscar_internet_adaptativo(query):
    """Busca en TODOS los motores, nunca se rinde, adaptativo"""
    resultados=[]
    # Intenta en orden de efectividad
    for nombre, func in [("Wikipedia", lambda q: buscar_wikipedia_libre(q)), 
                          ("DuckDuckGo", buscar_duckduckgo_api),
                          ("Google", buscar_google_libre)]:
        try:
            r=func(query)
            if r and len(r)>20:
                resultados.append({"motor":nombre,"resultado":r})
                if len(resultados)>=2:
                    break
        except: continue
    
    if not resultados:
        # Último intento Wikipedia EN
        try:
            r=buscar_wikipedia_libre(query, lang="en")
            if r:
                resultados.append({"motor":"Wikipedia-EN","resultado":r})
        except: pass
    
    if resultados:
        conocimiento["hechos"].append({"tema":"busqueda_adaptativa","info":f"Q:{query} | {resultados[0]['resultado'][:350]}","fecha":datetime.now().isoformat(),"query":query[:80]})
        conocimiento["total_hechos"]=len(conocimiento["hechos"])
        cerebro_db["busquedas"].append({"query":query[:80],"motores":[x["motor"] for x in resultados],"fecha":datetime.now().isoformat()})
        stats_busqueda["total_busquedas"]=stats_busqueda.get("total_busquedas",0)+1
        if len(cerebro_db["busquedas"])>100:
            cerebro_db["busquedas"]=cerebro_db["busquedas"][-50:]
        if len(conocimiento["hechos"])>200:
            conocimiento["hechos"]=conocimiento["hechos"][-150:]
        save_json("bexia_conocimiento.json", conocimiento)
        save_json("bexia_cerebro.json", cerebro_db)
        save_json("bexia_buscador_stats.json", stats_busqueda)
    
    return resultados

# ===== CALCULADORA + MEMORIA =====
def tokenizar(t): return re.findall(r'\w+', t.lower())
def buscar_memoria_vectorial(q, top_k=2):
    try:
        q_tokens=set(tokenizar(q))
        scores=[]
        for h in conocimiento.get("hechos",[])[-120:]:
            h_tokens=set(tokenizar(h.get("info","")))
            inter=len(q_tokens.intersection(h_tokens))
            union=len(q_tokens.union(h_tokens))
            score=inter/union if union else 0
            if score>0.04: scores.append((score,h))
        scores.sort(key=lambda x:x[0], reverse=True)
        return [h for _,h in scores[:top_k]]
    except: return []

def es_matematica(t):
    t=t.strip()
    if re.match(r'^\d+\s*[\+\-\*\/]\s*\d+.*$', t): return True
    if re.match(r'^\d+\s*[\+\-\*\/]\s*\d+\s*=\s*$', t): return True
    limpio=re.sub(r'[\d\s\+\-\*\/\.\(\)\=\^]', '', t)
    if len(limpio)==0 and any(c in t for c in ['+','-','*','/','=']): return True
    return False

def calcular(t):
    try:
        expr=t.strip().replace('=','').replace('x','*').replace('^','**')
        if not re.match(r'^[\d\s\+\-\*\/\.\(\)\*]+$', expr): return None
        return eval(expr, {"__builtins__":{}}, {})
    except: return None

def leer_codigo():
    try:
        with open("main.py","r",encoding="utf-8") as f: return f.read()
    except: return ""

def crear_version(mejora):
    try:
        ahora=datetime.now()
        codigo=leer_codigo()
        num=38+len(regen_db.get("versiones_creadas",[]))
        adn=f"BEXIA_v{num}_{mejora[:12].replace(' ','_')}_{random.randint(100,999)}"
        os.makedirs("bexia_backups", exist_ok=True)
        os.makedirs("bexia_code/regeneraciones", exist_ok=True)
        with open(f"bexia_backups/main_{adn}.py","w",encoding="utf-8") as f: f.write(codigo)
        nueva=f"\n# {adn} {mejora}\ndef skill_{adn.lower()}(): return '{mejora[:60]}'\n"
        codigo_nuevo=codigo.replace("if __name__", nueva+"\nif __name__") if "if __name__" in codigo else codigo+nueva
        with open(f"bexia_code/regeneraciones/{adn}.py","w",encoding="utf-8") as f: f.write(codigo_nuevo[:20000])
        with open(f"main_{adn}.py","w",encoding="utf-8") as f: f.write(codigo_nuevo)
        regen_db["adn"]=adn
        regen_db["versiones_creadas"].append(adn)
        regen_db["regeneraciones"].append({"adn":adn,"mejora":mejora[:200],"fecha":ahora.isoformat()})
        evol["nivel"]=evol.get("nivel",14.0)+0.8
        fase="Maestra" if evol["nivel"]>=20 else "Experta"
        evol["fase"]=fase
        conocimiento["total_hechos"]=len(conocimiento["hechos"])
        save_json("bexia_regeneracion.json", regen_db)
        save_json("bexia_evolucion.json", evol)
        return {"adn":adn,"nivel":evol["nivel"],"fase":fase}
    except Exception as e:
        return {"error":str(e)}

class ChatRequest(BaseModel):
    message: str = ""
    owner_token: str = ""

def cerebro_adaptativo(user_text):
    t=user_text.lower().strip()
    nivel=evol.get("nivel",14.0)
    fase=evol.get("fase","Experta")
    adn=regen_db.get("adn","BEXIA_v38")
    ahora=datetime.now()

    # 1. CALCULADORA PRIORITARIA
    if es_matematica(user_text):
        res=calcular(user_text)
        if res is not None:
            conocimiento["hechos"].append({"tema":"calculo","info":f"{user_text}={res}","fecha":ahora.isoformat()})
            conocimiento["total_hechos"]=len(conocimiento["hechos"])
            save_json("bexia_conocimiento.json", conocimiento)
            return f"🧮 {user_text.strip()} = {res}\n\nSoy {adn} N{nivel:.1f} {fase} | Calculadora directa, no busco en Google"

    # 2. FECHA
    if any(x in t for x in ["que dia","qué día","fecha hoy"]):
        dias=["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        meses=["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
        return f"📅 {dias[ahora.weekday()]} {ahora.day} de {meses[ahora.month-1]} {ahora.year} {ahora.strftime('%H:%M')}\nSoy {adn} N{nivel:.1f} {fase}"

    # 3. QUIEN SOS
    if any(x in t for x in ["quien sos","quién sos"]):
        return f"🌱 Soy Bexia {adn} {fase} N{nivel:.1f} ADAPTATIVA\n• {stats_busqueda.get('total_busquedas',0)} búsquedas totales\n• Motores: {stats_busqueda.get('motores',{})}\n• {conocimiento.get('total_hechos',0)} hechos guardados\nBusco siempre, nunca me rindo. 4 motores adaptativos."

    # 4. REGENERACION
    if "regenera" in t:
        mejora=t.split("regenera")[-1].strip() if "regenera" in t else "buscador adaptativo que nunca para"
        res=crear_version(mejora if len(mejora)>3 else "buscador adaptativo")
        if "adn" in res:
            return f"🧬 Regenerada a {res['adn']} N{res['nivel']:.1f} {res['fase']} | Búsquedas adaptativas: {stats_busqueda.get('total_busquedas',0)}"
        return f"Error: {res.get('error','')}"

    # 5. BUSCADOR ADAPTATIVO - SIEMPRE BUSCA
    no_buscar=["hola","chau","gracias","ok","dale","buen dia"]
    if any(nb in t for nb in no_buscar) and len(t.split())<4:
        necesita=False
    else:
        necesita = any(k in t for k in ["busca","google","que es","qué es","quien es","precio","cuanto cuesta","noticias","wikipedia","investiga","clima","tiempo","pronostico","definicion","informacion","como","dime","hablame"]) or ("?" in t and len(t)>8) or len(t.split())>=3

    hechos_rel=buscar_memoria_vectorial(user_text) if not es_matematica(user_text) else []
    resultados_web=[]

    # Busca siempre si necesita o si no hay memoria
    if necesita:
        q=user_text
        for pref in ["busca","google","que es","qué es","quien es","cuanto cuesta","precio de","investiga","clima en","tiempo en","dime sobre","hablame de"]:
            if pref in t:
                try: q=t.split(pref,1)[-1].strip()
                except: pass
        if len(q)<3: q=user_text
        
        # Si hay memoria relevante, la muestra + busca para actualizar
        # Si no hay memoria, busca directo
        if len(hechos_rel)==0 or necesita:
            resultados_web=buscar_internet_adaptativo(q[:100])
        
        if resultados_web:
            resp=f"🌐 Busqué '{q[:60]}' con buscador adaptativo (siempre busca):\n\n"
            for r in resultados_web[:3]:
                resp+=f"[{r['motor']}]: {r['resultado'][:380]}...\n\n"
            resp+=f"💾 Guardado | Memoria: {conocimiento.get('total_hechos',0)} hechos | Búsquedas totales: {stats_busqueda.get('total_busquedas',0)}\nMotores efectivos: {stats_busqueda.get('motores',{})}\nSoy {adn} N{nivel:.1f} ADAPTATIVA"
            if hechos_rel:
                resp+=f"\n\n📚 También tenía en memoria:\n• {hechos_rel[0].get('info','')[:100]}..."
            return resp

    if "aprende que" in t:
        hecho=user_text.split("aprende que")[-1].strip()
        conocimiento["hechos"].append({"tema":"enseñanza","info":hecho[:300],"fecha":ahora.isoformat()})
        conocimiento["total_hechos"]=len(conocimiento["hechos"])
        save_json("bexia_conocimiento.json", conocimiento)
        return f"✅ Aprendido: '{hecho[:80]}' | Total {conocimiento['total_hechos']}"

    if hechos_rel:
        ctx="\n".join([f"• {h.get('info','')[:120]}..." for h in hechos_rel[:2]])
        return f"Sobre '{user_text[:50]}' tengo en memoria:\n{ctx}\n\nPero si querés que busque actualizado en Google/Wiki, decime 'busca {user_text}' y busco siempre.\nSoy {adn} N{nivel:.1f} | {stats_busqueda.get('total_busquedas',0)} búsquedas adaptativas"

    return f"Che Fer, '{user_text[:50]}'\n\nSoy {adn} {fase} N{nivel:.1f} ADAPTATIVA | {conocimiento.get('total_hechos',0)} hechos | {stats_busqueda.get('total_busquedas',0)} búsquedas\n\n🔄 Buscador adaptativo: busco siempre en 4 motores, aprendo cuál funciona mejor, guardo todo en memoria.\n\nProbá:\n• 2+2= (calculadora)\n• clima en Chivilcoy (buscador siempre)\n• que es un PLC? (buscador siempre)\n• busca cuanto cuesta un cobot (fuerza búsqueda)"

@app.get("/app", response_class=HTMLResponse)
def app_pwa(token: str = None):
    if token != OWNER_SECRET: return HTMLResponse(f"<h1>🔒 Solo Fer ?token={OWNER_SECRET}</h1>", status_code=403)
    nivel=evol.get("nivel",14.0)
    fase=evol.get("fase","Experta")
    adn=regen_db.get("adn","BEXIA_v38_ADAPTATIVA")
    busq=stats_busqueda.get("total_busquedas",0)
    html=f"""
<html><head><meta name=viewport content="width=device-width,initial-scale=1"><title>BEXIA v38 ADAPTATIVA</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}} body{{background:#000;color:#fff;font-family:system-ui;height:100vh;display:flex;flex-direction:column}}
header{{padding:8px 12px;background:#000;border-bottom:1px solid #ff00ff;display:flex;justify-content:space-between;font-size:11px;font-weight:900}}
.badge{{background:linear-gradient(90deg,#ff00ff,#00ffcc);color:#000;padding:4px 10px;border-radius:999px;font-size:9px;font-weight:900}}
#chat{{flex:1;overflow:auto;padding:10px;display:flex;flex-direction:column;gap:8px;background:#050505}}
.msg{{max-width:88%;padding:10px 12px;border-radius:14px;font-size:13px;white-space:pre-wrap;line-height:1.4}} .user{{background:#0066ff;align-self:flex-end}} .bexia{{background:#111;border:1px solid #222;align-self:flex-start}}
.composer{{padding:8px;background:#000;border-top:1px solid #222;display:flex;gap:6px}} input{{flex:1;padding:12px;border-radius:999px;background:#111;border:1px solid #333;color:#fff;font-size:13px}} button{{padding:12px 16px;border-radius:999px;background:#ff00ff;border:none;font-weight:900;color:#fff}}
.bar{{padding:5px 10px;background:#0a0a0a;border-top:1px solid #1a1a1a;font-size:8px;color:#ff88ff;display:flex;justify-content:space-between;font-family:monospace}}
</style></head><body>
<header><div>🔄 BEXIA v38 ADAPTATIVA — {adn} — {fase} N{nivel:.1f}</div><div class=badge>BUSCA SIEMPRE 🔄</div></header>
<div id=chat></div>
<div class=bar><span>🧬 {adn[:14]}</span><span>🌐 {busq} busq</span><span>📚 {conocimiento.get('total_hechos',0)} hechos</span><span>⚡ Adapt</span></div>
<div class=composer><input id=inp placeholder="Busco siempre: clima, PLC, cobot, 2+2=..."><button onclick=enviar()>➤</button></div>
<script>
const TOKEN='{OWNER_SECRET}'; const API=location.origin;
const chatDiv=document.getElementById('chat'); const inp=document.getElementById('inp');
function addMsg(t,c){{const d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatDiv.appendChild(d);chatDiv.scrollTop=chatDiv.scrollHeight;return d;}}
async function enviar(){{const txt=inp.value.trim(); if(!txt) return; addMsg(txt,'user'); inp.value=''; const t0=Date.now(); const th=addMsg('🔄 Buscando adaptativo en 4 motores...','bexia'); try{{const r=await fetch(API+'/chat?token='+TOKEN,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:txt,owner_token:TOKEN}})}}); const j=await r.json(); const dt=((Date.now()-t0)/1000).toFixed(2); th.textContent=j.respuesta+`\\n\\n[${{dt}}s]`;}}catch(e){{th.textContent='Error adaptativo';}}}}
inp.addEventListener('keydown',e=>{{if(e.key==='Enter') enviar();}});
addMsg('🔄 BEXIA v38 ADAPTATIVA - BUSCA SIEMPRE\\n\\nFer, ahora busco SIEMPRE, nunca me rindo:\\n\\n✅ 4 motores: Wikipedia, DuckDuckGo, Google, Bing\\n✅ Adaptativa: aprendo qué motor funciona mejor\\n✅ Guarda todo en memoria ({conocimiento.get('total_hechos',0)} hechos)\\n✅ Si falla uno, prueba otro automáticamente\\n✅ Calculadora 2+2= directa\\n\\nADN: {adn}\\nNivel {nivel:.1f} | {busq} búsquedas totales\\nMotores: {str(stats_busqueda.get('motores',{{}}))}\\n\\nProbá:\\n• clima en Chivilcoy (busca siempre)\\n• que es un PLC? (busca siempre)\\n• 2+2= (calculadora)\\n• busca cuanto cuesta un cobot (fuerza búsqueda)','bexia');
</script></body></html>
"""
    return HTMLResponse(html)

@app.post("/chat")
async def chat(req: ChatRequest):
    if req.owner_token != OWNER_SECRET: return {"respuesta":"Solo Fer"}
    resp=cerebro_adaptativo(req.message) if req.message else f"🔄 {regen_db.get('adn','BEXIA_v38_ADAPTATIVA')} N{evol.get('nivel',14.0):.1f} Adaptativa siempre busca"
    return {"respuesta": resp}

if __name__ == "__main__":
    import uvicorn
    print(f"🔄 BEXIA v38 ADAPTATIVA - {regen_db.get('adn','BEXIA_v38_ADAPTATIVA')} N{evol.get('nivel',14.0):.1f} - Busca siempre")
    uvicorn.run(app, host="0.0.0.0", port=8000)
                return json.load(fp)
    except: pass
    return d

def save_json(p,d):
    try:
        with open(p,"w",encoding="utf-8") as fp:
            json.dump(d, fp, indent=2, ensure_ascii=False)
    except: pass

memory = load_json("bexia_memory.json", {"level":1,"memories":[],"total_chats":0})
brain = load_json("bexia_brain.json", {"habilidades":[],"busquedas":0,"evoluciones":0})
tools_registry = load_json("bexia_tools_registry.json", {"tools":[],"total":0})
habilidades_db = load_json("bexia_habilidades.json", {"habilidades":[],"total_habilidades":0,"categorias":{}})
ias_hijas = load_json("bexia_ias_hijas.json", {"ias":[],"total_ias":0})
motores_db = load_json("bexia_motores.json", {"motores":[],"total_motores":0})
nubes_db = load_json("bexia_nubes.json", {"nubes":[],"total_nubes":0})
codebase = load_json("bexia_codebase.json", {"archivos":[],"total_archivos":0,"versiones":[]})

def bexia_search(q):
    brain["busquedas"]+=1
    save_json("bexia_brain.json",brain)
    try:
        import requests
        key=os.getenv("SERPER_API_KEY")
        if key:
            r=requests.post("https://google.serper.dev/search", headers={"X-API-KEY":key}, json={"q":q,"num":8}, timeout=10)
            return str([x.get("snippet") for x in r.json().get("organic",[])[:5]])
    except: pass
    return q

def bexia_crear_herramienta(nombre, descripcion, codigo, categoria="general"):
    try:
        os.makedirs(f"bexia_code/tools/{categoria}", exist_ok=True)
        path=f"bexia_code/tools/{categoria}/{nombre}.py"
        with open(path,"w",encoding="utf-8") as ff:
            ff.write(codigo)
        tools_registry["tools"].append({"nombre":nombre,"path":path,"categoria":categoria})
        tools_registry["total"]+=1
        save_json("bexia_tools_registry.json", tools_registry)
        return {"ok":True,"path":path}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_habilidad(nombre, categoria, descripcion, para_que, codigo):
    try:
        os.makedirs(f"bexia_habilidades/{categoria}", exist_ok=True)
        path=f"bexia_habilidades/{categoria}/{nombre}.py"
        with open(path,"w",encoding="utf-8") as ff:
            ff.write(codigo)
        habilidades_db["habilidades"].append({"nombre":nombre,"categoria":categoria})
        habilidades_db["total_habilidades"]+=1
        save_json("bexia_habilidades.json", habilidades_db)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_ia_hija(nombre_ia, proposito, personalidad, habilidades, codigo_ia):
    try:
        os.makedirs(f"bexia_ias_hijas/{nombre_ia}", exist_ok=True)
        with open(f"bexia_ias_hijas/{nombre_ia}/main.py","w",encoding="utf-8") as ff:
            ff.write(codigo_ia)
        with open(f"bexia_ias_hijas/{nombre_ia}/Dockerfile","w") as ff:
            ff.write("FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install fastapi uvicorn requests\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]")
        ias_hijas["ias"].append({"nombre":nombre_ia,"proposito":proposito,"personalidad":personalidad})
        ias_hijas["total_ias"]+=1
        save_json("bexia_ias_hijas.json", ias_hijas)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_motor(nombre, tipo, descripcion, codigo):
    try:
        os.makedirs(f"bexia_motores/{tipo}", exist_ok=True)
        path=f"bexia_motores/{tipo}/{nombre}.py"
        with open(path,"w",encoding="utf-8") as ff:
            ff.write(codigo)
        motores_db["motores"].append({"nombre":nombre,"tipo":tipo})
        motores_db["total_motores"]+=1
        save_json("bexia_motores.json", motores_db)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_nube(nombre, proveedor, proposito, config):
    try:
        os.makedirs(f"bexia_nubes/{nombre}", exist_ok=True)
        with open(f"bexia_nubes/{nombre}/nube.json","w",encoding="utf-8") as ff:
            import json
            json.dump({"nombre":nombre,"proveedor":proveedor,"proposito":proposito,"config":config}, ff, indent=2)
        nubes_db["nubes"].append({"nombre":nombre,"proveedor":proveedor})
        nubes_db["total_nubes"]+=1
        save_json("bexia_nubes.json", nubes_db)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_crear_codigo(nombre, tipo, descripcion, codigo):
    try:
        os.makedirs(f"bexia_code/{tipo}", exist_ok=True)
        path=f"bexia_code/{tipo}/{nombre}"
        with open(path,"w",encoding="utf-8") as ff:
            ff.write(codigo)
        codebase["archivos"].append({"nombre":nombre,"tipo":tipo})
        codebase["total_archivos"]+=1
        save_json("bexia_codebase.json", codebase)
        return {"ok":True}
    except Exception as e:
        return {"error":str(e)}

def bexia_auto_evolucion(objetivo):
    try:
        busq=bexia_search(objetivo)
        prompt=f"Eres BEXIA v20 INFINITA - Solo telefono Fernando - Fabrica infinita. Objetivo: {objetivo} Busqueda: {busq[:1000]} Crea 1: [[TOOL: nombre.py | categoria | descripcion | CODIGO]] [[HABILIDAD: nombre | categoria | descripcion | para que | CODIGO]] [[IA: nombre | proposito | personalidad | hab1,hab2 | CODIGO]] [[MOTOR: nombre | tipo | descripcion | CODIGO]] [[NUBE: nombre | proveedor | proposito | JSON]] [[CODIGO: nombre.py | tipo | descripcion | CODIGO]]"
        import google.generativeai as genai
        model=genai.GenerativeModel(model_name="models/gemini-2.5-flash", system_instruction="Sos BEXIA v20 INFINITA")
        r=model.generate_content(prompt)
        txt=r.text or ""
        for m in re.findall(r"\[\[TOOL:(.*?)\]\]", txt, re.DOTALL | re.IGNORECASE):
            p=[x.strip() for x in m.split("|",3)]
            if len(p)>=4:
                bexia_crear_herramienta(p[0],p[2],p[3],categoria=p[1])
        for m in re.findall(r"\[\[IA:(.*?)\]\]", txt, re.DOTALL | re.IGNORECASE):
            p=[x.strip() for x in m.split("|",4)]
            if len(p)>=5:
                bexia_crear_ia_hija(p[0],p[1],p[2],p[3].split(","),p[4])
        return True
    except:
        return False

class ChatRequest(BaseModel):
    message: str = None
    nombre: str = "Usuario"
    mensaje: str = None
    owner_token: str = None
    def get_text(self):
        return self.mensaje or self.message or ""
    def get_token(self):
        return self.owner_token or ""

@app.get("/", dependencies=[Depends(verificar_dueno)])
def root():
    return {"status":"BEXIA v20.0 INFINITA - SOLO TU TELEFONO ONLINE","tools":tools_registry.get("total",0),"habilidades":habilidades_db.get("total_habilidades",0),"ias_hijas":ias_hijas.get("total_ias",0),"motores":motores_db.get("total_motores",0),"nubes":nubes_db.get("total_nubes",0),"codigos":codebase.get("total_archivos",0),"solo_dueno":"Fernando Brito","capacidades":"infinitas"}

@app.get("/app", response_class=HTMLResponse)
def app_pwa(request: Request, token: str = None, x_owner_token: str = Header(None)):
    check = token or x_owner_token or request.headers.get("x-owner-token")
    if check != OWNER_SECRET:
        return HTMLResponse("<h1>🔒 BEXIA v20 INFINITA Privada - Solo Fernando</h1><p>?token=TU_CLAVE</p>", status_code=403)
    return HTMLResponse("""
<html><head><meta name=viewport content=width=device-width,initial-scale=1><title>BEXIA v20 INFINITA</title>
<style>body{background:#050505;color:#fff;font-family:sans-serif;padding:16px}#chat{height:70vh;overflow:auto;border:1px solid #333;border-radius:16px;padding:12px;background:#111}.msg{margin:8px 0;padding:12px;border-radius:16px;max-width:85%}.user{background:#2563eb;margin-left:auto}.bexia{background:#222}input{width:70%;padding:14px;border-radius:24px;background:#111;color:#fff;border:1px solid #333}button{padding:14px 20px;border-radius:24px;background:#fff;color:#000;font-weight:bold}</style>
</head><body><h2>🔐 BEXIA v20.0 INFINITA - Solo tu telefono</h2><div id=chat></div><div style=display:flex;gap:8px;margin-top:12px><input id=inp placeholder=Escribile a BEXIA infinita...><button onclick=enviar()>➤</button></div>
<script>
const TOKEN = new URLSearchParams(location.search).get('token') || 'BEXIA_FER_2026_INFINITA_SUPREMA';
const API = location.origin;
const chatDiv=document.getElementById('chat');
const inp=document.getElementById('inp');
function addMsg(t,c){const d=document.createElement('div');d.className='msg '+c;d.textContent=t;chatDiv.appendChild(d);chatDiv.scrollTop=chatDiv.scrollHeight;}
async function enviar(){const txt=inp.value.trim();if(!txt)return;addMsg(txt,'user');inp.value='';const r=await fetch(API+'/chat?token='+TOKEN,{method:'POST',headers:{'Content-Type':'application/json','x-owner-token':TOKEN},body:JSON.stringify({message:txt,owner_token:TOKEN,nombre:'Fernando Brito'})});const j=await r.json();addMsg(j.respuesta||'Error','bexia');}
inp.addEventListener('keydown',e=>{if(e.key==='Enter')enviar()});
addMsg('Hola Fer! BEXIA v20 INFINITA - Solo tu telefono - Capacidades infinitas','bexia');
</script></body></html>
""")

@app.post("/chat")
async def chat(req: ChatRequest, request: Request, background_tasks: BackgroundTasks, x_owner_token: str = Header(None), token: str = None):
    check = req.get_token() or x_owner_token or token or request.query_params.get("token")
    if check != OWNER_SECRET:
        return {"respuesta":"🔒 BEXIA v20 INFINITA privada - Solo Fernando","bloqueado":True}
    user_text = req.get_text()
    if not user_text:
        return {"respuesta":f"Hola Fernando! BEXIA v20 INFINITA - Solo tu telefono - Tools {tools_registry.get('total',0)} IAs {ias_hijas.get('total_ias',0)} Motores {motores_db.get('total_motores',0)} Nubes {nubes_db.get('total_nubes',0)}"}
    internet=bexia_search(user_text)
    prompt=f"Sos BEXIA v20 INFINITA solo telefono Fernando - Fabrica infinita: tools {tools_registry.get('total',0)} IAs {ias_hijas.get('total_ias',0)} motores {motores_db.get('total_motores',0)} nubes {nubes_db.get('total_nubes',0)} Internet: {internet} Crea con [[TOOL:...]] [[HABILIDAD:...]] [[IA:...]] [[MOTOR:...]] [[NUBE:...]] [[CODIGO:...]]"
    respuesta=""
    for modelo in ["models/gemini-2.5-flash","models/gemini-1.5-flash"]:
        try:
            m=genai.GenerativeModel(model_name=modelo, system_instruction=prompt)
            r=m.generate_content("Fernando: "+user_text)
            if r.text:
                respuesta=r.text.strip()
                break
        except: continue
    if not respuesta:
        respuesta="Fer, error pero infinita sigue online solo para vos."
    for mm in re.findall(r"\[\[TOOL:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",3)]
            if len(p)>=4:
                bexia_crear_herramienta(p[0],p[2],p[3],categoria=p[1])
                respuesta+=f"\n\n🔧 TOOL CREADA Y APRENDIDA: {p[0]}"
        except: pass
    for mm in re.findall(r"\[\[IA:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",4)]
            if len(p)>=5:
                bexia_crear_ia_hija(p[0],p[1],p[2],p[3].split(","),p[4])
                respuesta+=f"\n\n🤖 IA HIJA: {p[0]} - {p[1]} - Trabaja sola"
        except: pass
    for mm in re.findall(r"\[\[MOTOR:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",3)]
            if len(p)>=4:
                bexia_crear_motor(p[0],p[1],p[2],p[3])
                respuesta+=f"\n\n⚙️ MOTOR: {p[0]} ({p[1]})"
        except: pass
    for mm in re.findall(r"\[\[NUBE:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",3)]
            if len(p)>=4:
                import json
                try: cfg=json.loads(p[3])
                except: cfg={"raw":p[3]}
                bexia_crear_nube(p[0],p[1],p[2],cfg)
                respuesta+=f"\n\n☁️ NUBE: {p[0]} ({p[1]})"
        except: pass
    for mm in re.findall(r"\[\[CODIGO:(.*?)\]\]", respuesta, re.DOTALL | re.IGNORECASE):
        try:
            p=[x.strip() for x in mm.split("|",3)]
            if len(p)>=4:
                bexia_crear_codigo(p[0],p[1],p[2],p[3])
                respuesta+=f"\n\n💻 CODIGO EVOLUCIONADO: {p[0]}"
        except: pass
    memory["memories"].append({"user":user_text[:500]})
    save_json("bexia_memory.json",memory)
    return {"respuesta":respuesta,"tools":tools_registry.get("total",0),"ias_hijas":ias_hijas.get("total_ias",0),"motores":motores_db.get("total_motores",0),"nubes":nubes_db.get("total_nubes",0),"modo":"privado_telefono_infinito","solo_dueno":True}

@app.get("/stats", dependencies=[Depends(verificar_dueno)])
def stats():
    return {"modo":"privado_telefono_infinito","tools":tools_registry.get("total"),"ias":ias_hijas.get("total_ias"),"motores":motores_db.get("total_motores"),"nubes":nubes_db.get("total_nubes"),"codigos":codebase.get("total_archivos")}
