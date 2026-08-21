# -*- coding: utf-8 -*-
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
        api_key_fija = "AQ.Ab8RN6I0m8y96CV2_JbvMovYlEzJs1yFEiGZNEWWNnJt3pQiMw"
        
        client = genai.Client(api_key=api_key_fija)
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=user_message,
            config={
                "system_instruction": "Eres Bexia, una entidad digital autonoma creada por Fer."
            }
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Error neural: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
