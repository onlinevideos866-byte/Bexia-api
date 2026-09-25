# main.py - Este es el que compila a APK con buildozer.spec
# Pega este codigo en main.py (minuscula) en la carpeta de tu app
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import requests, json, os

BEXIA_URL = "http://127.0.0.1:11434"  # Ollama local, BEXIA vive ahi

class BexiaApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self.add_widget(Label(text='BEXIA AUTONOMA v1', font_size=28, size_hint_y=0.15))
        self.entrada = TextInput(hint_text='Ej: creame una app calculadora', size_hint_y=0.2, multiline=False)
        self.add_widget(self.entrada)
        self.salida = Label(text='BEXIA esperando...\nEscribe arriba y toca EJECUTAR', size_hint_y=0.5, halign='left')
        self.add_widget(self.salida)
        btn = Button(text='EJECUTAR CON BEXIA', size_hint_y=0.15, background_color=(0.2,0.8,0.2,1))
        btn.bind(on_press=self.ejecutar)
        self.add_widget(btn)
        btn2 = Button(text='MODO VIGIA (evoluciona sola)', size_hint_y=0.1)
        btn2.bind(on_press=self.vigia)
        self.add_widget(btn2)

    def ejecutar(self, instance):
        orden = self.entrada.text
        if not orden:
            self.salida.text = "Escribe una orden primero"
            return
        self.salida.text = f"BEXIA pensando: {orden}..."
        try:
            # Le pega a Ollama / BEXIA
            r = requests.post(f"{BEXIA_URL}/api/chat", json={
                "model":"qwen2:0.5b",
                "messages":[{"role":"user","content":orden}],
                "stream":False
            }, timeout=30)
            resp = r.json()["message"]["content"]
            self.salida.text = f"BEXIA:\n{resp[:500]}"
        except Exception as e:
            self.salida.text = f"Error: {e}\nAsegurate de tener 'ollama serve' y 'python bexia.py' corriendo en Termux"

    def vigia(self, instance):
        self.salida.text = "MODO VIGIA ACTIVADO\nBEXIA ahora evoluciona cada 10 min\nMira bexia.log en Termux"

class MainApp(App):
    def build(self):
        return BexiaApp()

if __name__ == "__main__":
    MainApp().run()
