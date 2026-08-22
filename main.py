import os, json, datetime
from fastapi import FastAPI, Request
import gspread
from google.oauth2.service_account import Credentials
from google import genai  # NUEVA LIBRERIA

app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Memoria BEXIA")

# GEMINI NUEVO
client_ai = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def get_sheet():
    try:
        creds_dict = json.loads(GOOGLE_CREDS_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds).open(SHEET_NAME).sheet1
    except Exception as e:
        print(e)
        return None

def guardar(nombre, tel, msg, resp):
    try:
        sh = get_sheet()
        if not sh: return
        if len(sh.get_all_values())==0:
            sh.append_row(["Fecha","Nombre","Telefono","Mensaje","Respuesta BEXIA"])
        sh.append_row([datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), nombre, tel, msg, resp])
    except Exception as e:
        print(e)

@app.get("/")
def home():
    return {"status":"BEXIA VIVA"}

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    msg = data.get("mensaje") or data.get("message") or ""
    nombre = data.get("nombre") or "Cliente"
    tel = data.get("telefono") or "000"

    try:
        r = client_ai.models.generate_content(model="gemini-1.5-flash", contents=f"Sos BEXIA, vendedor argentino, cliente {nombre} dice: {msg}")
        respuesta = r.text
    except Exception as e:
        respuesta = f"Hola {nombre}! Soy BEXIA. {e}"

    guardar(nombre, tel, msg, respuesta)
    return {"respuesta": respuesta}

# ESTO ES LO QUE FALTABA PARA QUE NO SE APAGUE
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
