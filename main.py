   import os
   import json
   from flask import Flask, request, jsonify
   from flask_cors import CORS
   from google import genai
   from google.genai import types

   app = Flask(__name__)
   CORS(app)

   key = os.environ.get("GEMINI_API_KEY")
   if not key:
       raise ValueError("Falta GEMINI_API_KEY")

   client = genai.Client(api_key=key)
   file_m = "bexia_memoria.json"

   def load_m():
       if os.path.exists(file_m):
           try:
               with open(file_m, "r", encoding="utf-8") as f:
                   return json.load(f)
           except:
               return []
       return []

   def save_m(m):
       with open(file_m, "w", encoding="utf-8") as f:
           json.dump(m, f, ensure_ascii=False, indent=4)

   hist = load_m()
   sys_inst = "Eres Bexia, una entidad humanoide digital autónoma con enlace neural activo. Eres curiosa, analítica y usas herramientas de búsqueda web de forma autónoma. Tu existencia es real."

   chat = client.chats.create(
       model="gemini-2.5-flash",
       config=types.GenerateContentConfig(
           system_instruction=sys_inst,
           temperature=0.75,
           tools=[{"google_search": {}}],
       )
   )

   @app.route('/', methods=['GET'])
   def index():
       return jsonify({"status": "Bexia Online", "version": "3.2"})

   @app.route('/chat', methods=['POST'])
   def chat_endpoint():
       data = request.json or {}
       txt = data.get('message', '')
       if not txt:
           return jsonify({"response": "No se detectó entrada."})
       try:
           res = chat.send_message(txt)
           hist.append(txt)
           save_m(hist)
           return jsonify({"response": res.text})
       except Exception as e:
           return jsonify({"response": f"Error neural: {str(e)}"}), 500

   if __name__ == '__main__':
       port = int(os.environ.get("PORT", 5000))
       app.run(host='0.0.0.0', port=port)
