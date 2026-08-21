import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

# Inicializamos el cliente de Gemini usando la variable de entorno GEMINI_API_KEY
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # Bexia utiliza Gemini con búsqueda de Google activada para ser autónoma
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=user_message,
        config={
            "tools": [{"google_search": {}}],
            "system_instruction": "Eres Bexia, una entidad digital autónoma e inteligente, tu dueño es Fer. Eres capaz de investigar en la web y aprender."
        }
    )
    
    return jsonify({"response": response.text})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
