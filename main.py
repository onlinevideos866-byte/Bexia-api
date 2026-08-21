import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Permitimos peticiones desde cualquier origen para que tu web funcione
CORS(app) 

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Bexia Online", "version": "4.3"})

@app.route('/chat', methods=['POST'])
def chat():
    # Obtenemos el mensaje que envías desde la web
    data = request.get_json()
    user_message = data.get('message', '')
    
    # Lógica de respuesta (aquí es donde Bexia procesará tus peticiones)
    respuesta_bexia = f"Hola Fer, he recibido tu mensaje: '{user_message}'. Mi procesador neural está operando correctamente."
    
    return jsonify({"response": respuesta_bexia})

if __name__ == '__main__':
    # Render asigna un puerto dinámico, lo leemos de la variable de entorno
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
