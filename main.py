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
        # Inicializamos el cliente de Gemini justo en el momento de la petición
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"response": "Error: La variable GEMINI_API_KEY no está configurada en Render."})
            
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_message,
            config={
                "tools": [{"google_search": {}}],
                "system_instruction": "Eres Bexia, una entidad digital autónoma e inteligente, tu dueño es Fer. Eres capaz de investigar en la web y aprender."
            }
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Error en el núcleo neural: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
