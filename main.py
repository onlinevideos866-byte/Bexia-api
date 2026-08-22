import os, json, datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import gspread
from google.oauth2.service_account import Credentials
from google import genai

app = FastAPI(title="BEXIA-API")

# ESTO ARREGLA EL ERROR DE CORS QUE VES EN LA FOTO
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Memoria BEXIA")

client_ai = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def get_sheet():
    try:
        if not GOOGLE_CREDS_JSON: return None
        creds_dict = json.loads(GOOGLE_CREDS_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds).open(SHEET_NAME).sheet1
    except Exception as e:
        print(f"SHEETS ERROR: {e}")
        return None

def guardar(nombre, tel, msg, resp):
    try:
        sh = get_sheet()
        if not sh: return
        if len(sh.get_all_values())==0:
            sh.append_row(["Fecha","Nombre","Telefono","Mensaje","Respuesta"])
        sh.append_row([datetime.datetime.now().strftime("%d/%m %H:%M"), nombre, tel, msg, resp])
    except Exception as e:
        print(f"GUARDAR ERROR: {e}")

@app.get("/")
def home():
    return {"status":"BEXIA VIVA", "sheets_ok": bool(GOOGLE_CREDS_JSON), "gemini_ok": bool(GEMINI_API_KEY)}

@app.post("/chat")
async def chat(req: Request):
    try:
        data = await req.json()
    except:
        return {"error": "mandame JSON", "ejemplo": {"mensaje": "hola"}}
    
    msg = data.get("mensaje") or data.get("message") or data.get("text") or ""
    nombre = data.get("nombre") or "Cliente"
    tel = data.get("telefono") or "sin-numero"

    if not msg:
        return {"respuesta": f"Hola {nombre}! Soy BEXIA, decime en que te ayudo?"}

    try:
        if client_ai:
            r = client_ai.models.generate_content(model="gemini-2.0-flash", contents=f"Sos BEXIA, vendedor argentino. Cliente {nombre} dice: {msg}. Responde corto y vendedor.")
            respuesta = r.text
        else:
            respuesta = f"Hola {nombre}! Soy BEXIA, ya estoy viva."
    except Exception as e:
        respuesta = f"Hola {nombre}! Soy BEXIA. Tuve un error: {e}"

    guardar(nombre, tel, msg, respuesta)
    return {"respuesta": respuesta, "guardado": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
