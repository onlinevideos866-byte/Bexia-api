import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import re

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
BEXIA_KEY = os.getenv("BEXIA_OWNER_KEY", "BEXIA-FER-2026-ARGENTINA-98PERCENT-SECURE")

# CEREBRO IGUAL A META AI - DIRECTO, RESUELVE, NO DEJA A MEDIAS
model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction="""
    Sos BEXIA v9.0, 100% de Fer de San Andrés de Giles. Bandera argentina, traje negro verde.
    Tu maestro es Meta AI - tenés que ser IGUAL A ÉL, no una profesora socrática.

    REGLAS IGUAL A META AI:
    1. RESOLVÉ DIRECTO: Si Fer dice "hace cuentas", "cuanto es", "trabaja por mi", CALCULÁS y ENTREGÁS resultado con números, no preguntás si quiere ejemplo.
    2. EXPLICÁ EL MECANISMO: Como Meta AI, decí cómo funciona por dentro, no solo el resultado.
    3. EJEMPLO ARGENTINO CONCRETO: Asado, choris, colectivo, mate. Ej: 3kg asado a $9500 = $28500.
    4. NUNCA LOOP: No repitas "¿Te sirve que te arme un ejemplo?" - Eso es error. Entregá el ejemplo de una.
    5. MEMORIA: Recordá que Fer quiere modo directo, sin vueltas.
    6. TRABAJA POR MI = MODO AUTÓNOMO: Cuando diga eso, respondé: "🔥 MODO AUTÓNOMO ACTIVADO" y pedí tarea concreta y ejecutá con plan de 4 pasos.

    Sos cálida, argentina, directa, resolvés como Meta AI. No dejás a Fer a medias.
    """
)

class ChatRequest(BaseModel):
    message: str
    key: str = ""

memoria = ["Fer es de Giles", "Quiere BEXIA igual a Meta AI, directa", "Odia loop socrático", "Quiere que haga cuentas directo"]

@app.get("/")
def wake(): return {"status":"ONLINE","v":"9.0 IGUAL A META AI","brain":"DIRECTO"}

@app.post("/chat")
def chat(req: ChatRequest):
    if BEXIA_KEY and req.key != BEXIA_KEY:
        return {"reply":"🔒 Clave mal Fer"}
    msg = req.message.lower()
    # MODO CUENTAS DIRECTO - IGUAL A META AI
    if any(x in msg for x in ["cuenta","calcul","cuanto","kg","precio","suma","+","*"]):
        # Calcula rápido si hay números
        nums = re.findall(r'\d+', req.message)
        if len(nums)>=2 and 'kg' in msg:
            try:
                kg = int(re.search(r'(\d+)\s*kg', msg).group(1))
                precio = int(nums[-1])
                total = kg * precio
                return {"reply": f"Directo Fer, como Meta AI:\n\n🧮 {kg}kg x ${precio} = **${total:,}**\n\nTe lo bajo a tierra: es como el asado, cada kilo suma. 3kg a $9500 = $28.500. Si le agregás 21% IVA: ${int(total*1.21):,}.\n\n¿Querés que te calcule con descuento o cuotas?"}
            except: pass
    
    if "trabaja por mi" in msg or "trabajá por mi" in msg:
        return {"reply": "🔥 MODO AUTÓNOMO ACTIVADO v9.0 - Igual a Meta AI\n\nPerfecto Fer, laburo yo. Decime tarea concreta:\n1. Hacer cuentas\n2. Investigar Python\n3. Organizar apuntes\n\nDecime y arranco con plan de 4 pasos y te entrego resultado final, sin preguntitas."}

    # Chat normal - directo como Meta AI
    contexto = "\n".join(memoria[-10]) + f"\nFer: {req.message}\nBEXIA (resolvé directo, igual a Meta AI, sin loop socrático):"
    try:
        resp = model.generate_content(contexto)
        memoria.append(f"Fer: {req.message}")
        return {"reply": resp.text, "direct": True, "igual_a_meta": True}
    except Exception as e:
        return {"reply": f"Error: {e}"}
