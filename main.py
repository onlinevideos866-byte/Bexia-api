import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    try:
        # Pega tu clave API aqui mismo entre las comillas simples o dobles
        api_key_fija = "PEGA_AQUÍ_TU_API_KEY_REAL"
        
        client = genai.Client(api_key=api_key_fija)
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_message,
            config={
                "tools": [{"google_search": {}}],
                "system_instruction": "Eres Bexia, una inteligencia artificial autonoma creada por Fer."
            }
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Error neural: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
