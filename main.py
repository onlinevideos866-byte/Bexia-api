import os
import json
import datetime
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BEXIA-API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENV VARS de Render ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY") or os.getenv("Gemini...")
BEXIA_KEY = os.getenv("BEXIA_OWNER_KEY") or os.getenv("AQ.A...")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Memoria BEXIA")

# --- CONFIG GEMINI ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

# --- FUNCIONES SHEETS ---
def get_sheet():
    try:
        if not GOOGLE_CREDS_JSON:
            return None
        creds_dict = json.loads(GOOGLE_CREDS_JSON)
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sh = client.open(SHEET_NAME)
        return sh.sheet1
    except Exception as e:
        print(f"Error get_sheet: {e}")
        return None

def guardar_en_sheets(nombre, telefono, mensaje, respuesta):
    try:
        sheet = get_sheet()
        if not sheet:
            print("No hay sheet")
            return
        ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        valores = sheet.get_all_values()
        if len(valores) == 0:
            sheet.append_row(["Fecha", "Nombre", "Telefono", "Mensaje Cliente", "Respuesta BEXIA"])
        sheet.append_row([ahora, str(nombre), str(telefono), str(mensaje), str(respuesta)])
        print("OK Guardado en Sheets")
    except Exception as e:
        print(f"Error guardar_en_sheets: {e}")

# --- ENDPOINTS ---
@app.get("/")
def home():
    return {"status": "BEXIA VIVA", "sheets": bool(GOOGLE_CREDS_JSON), "gemini": bool(GEMINI_API_KEY)}

@app.post("/chat")
async def chat(request: Request, x_bexia_key: str = Header(None)):
    # Validacion de dueño opcional
    if BEXIA_KEY and x_bexia_key and x_bexia_key != BEXIA_KEY:
        raise HTTPException(status_code=401, detail="Key invalida")
    
    data = await request.json()
    mensaje = data.get("mensaje") or data.get("message") or data.get("text") or ""
    nombre = data.get("nombre") or data.get("name") or "Cliente"
    telefono = data.get("telefono") or data.get("phone") or data.get("from") or "sin-numero"

    if not mensaje:
        return {"error": "sin mensaje"}

    # --- PROMPT BEXIA ---
    prompt_bexia = f"""
    Sos BEXIA, asistente de ventas de Fernando. 
    Cliente: {nombre} ({telefono})
    Mensaje: {mensaje}
    Respondé corto, vendedor, cercano, argentino.
    """

    try:
        if model:
            resp = model.generate_content(prompt_bexia)
            respuesta = resp.text
        else:
            respuesta = "Hola! Soy BEXIA, en un momento te atiende Fernando."
    except Exception as e:
        respuesta = f"Estoy reconectando, reintentá en 10 seg. Error: {e}"

    # Guardar en Sheets AUTOMATICAMENTE
    guardar_en_sheets(nombre, telefono, mensaje, respuesta)

    return {"respuesta": respuesta, "guardado_sheets": True}

@app.post("/webhook")
async def webhook(request: Request):
    # Para WhatsApp/Twilio/WATI - usa el mismo que /chat
    return await chat(request)
