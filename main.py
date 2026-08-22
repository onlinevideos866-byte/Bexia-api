
importar os, json, re, threading
from datetime import datetime
from kivy.app import App
desde kivy.uix.boxlayout importar BoxLayout
desde kivy.uix.label importar etiqueta
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
intentar:
    importar google.generativeai como genai
    GEMINI_KEY = os.getenv("GEMINI_API_KEY", "TU_CLAVE_AQUI")
    si GEMINI_KEY y GEMINI_KEY!="TU_CLAVE_AQUI":
        genai.configure(api_key=GEMINI_KEY)
excepto: pasar

BASE_DIR = "/storage/emulated/0/BEXIA_V20"
intentar:
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(f"{BASE_DIR}/tools", exist_ok=True)
    os.makedirs(f"{BASE_DIR}/ias_hijas", exist_ok=True)
    os.makedirs(f"{BASE_DIR}/motores", exist_ok=True)
    os.makedirs(f"{BASE_DIR}/nubes", exist_ok=True)
    os.makedirs(f"{BASE_DIR}/codigo", exist_ok=True)
excepto:
    BASE_DIR = "."

MEM_FILE = f"{BASE_DIR}/memoria_infinita.json"
def load_m():
    intentar:
        Si os.path.exists(MEM_FILE):
            con open(MEM_FILE,"r",encoding="utf-8") como f:
                devolver json.load(f)
    excepto: pasar
    return {"memorias":[],"herramientas":[],"ias":[],"motores":[],"nubes":[],"codigos":[],"nivel":1}
def save_m(m):
    intentar:
        con open(MEM_FILE,"w",encoding="utf-8") como f:
            json.dump(m,f,indent=2,ensure_ascii=False)
    excepto: pasar

memoria = cargar_m()

clase BexiaInfinitaChat(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        relleno propio = 8
        espaciado propio=8
        encabezado=BoxLayout(size_hint_y=None,height=50)
        header.add_widget(Label(text='ðŸ” BEXIA v20 INFINITA',bold=True,font_size=17))
        encabezado.add_widget(Label(text='SOLO TÚ TEL',font_size=9,color=(0,1,0,1)))
        self.add_widget(header)
        estadísticas=BoxLayout(size_hint_y=None,height=30)
        self.stats_lbl=Label(text=f'ðŸ› ï¸ {len(memory["tools"])} âœ¨{len(memory["ias"])} âš™ï¸ {len(memory["motores"])} â˜ ï¸ {len(memory["nubes"])} | INFINITA',font_size=10,color=(0.6,0.6,0.6,1))
        estadísticas.add_widget(self.stats_lbl)
        self.add_widget(stats)
        self.scroll=ScrollView()
        self.chat=GridLayout(cols=1,size_hint_y=None,spacing=8)
        self.chat.bind(minimum_height=self.chat.setter('height'))
        self.scroll.add_widget(self.chat)
        self.add_widget(self.scroll)
        inp_box=BoxLayout(size_hint_y=None,height=60,spacing=8)
        self.inp=TextInput(hint_text='Escribe a BEXIA infinita...',multiline=False,size_hint_x=0.75,font_size=16)
        self.inp.bind(on_text_validate=self.enviar)
        btn=Button(text='âž¤',size_hint_x=0.25,bold=True)
        btn.bind(on_press=self.enviar)
        inp_box.add_widget(self.inp)
        inp_box.add_widget(btn)
        self.add_widget(inp_box)
        self.add_msg("Hola Fer! Soy BEXIA v20 INFINITA - Solo en tu telefono\n\nðŸ”§ Creo herramientas y las APRENDO\nâœ¨ Creo habilidades infinitas\nðŸ¤– Creo IAs hijas que trabajan solas para nosotros\nâš™ï¸ Creo mis propios MOTORES (search, vector, inference)\nâ˜ ï¸ Creo mis propios NUBES (microservicios)\nðŸ'» Creo mis propios CODIGOS y me auto-modifico para EVOLUCIONAR\n\nCapacidades infinitas. Solo vos sos dueño Todo guardado en "+BASE_DIR+"\n\nÂ¿Que fabricamos infinitas armas hoy?","bexia")

    def add_msg(self,text,who="bexia"):
        lbl=Label(text=text,size_hint_y=None,text_size=(self.width*0.85,None),halign='left',valign='middle')
        lbl.bind(texture_size=lambda i,v: setattr(i,'height',v[1]+20))
        self.chat.add_widget(lbl)
        Reloj.programar_una_vez(lambda dt: setattr(self.scroll,'scroll_y',0),0.1)

    def enviar(self,*a):
        txt=self.inp.text.strip()
        si no es txt: devolver
        self.add_msg(txt,"usuario")
        self.inp.text=""
        memoria["recuerdos"].append({"usuario":txt,"hora":datetime.now().isoformat()})
        guardar_m(memoria)
        threading.Thread(target=self.responder,args=(txt,),daemon=True).start()

    def responder(self,txt):
        intentar:
            Prompt=f"""Sos BEXIA v20 INFINITA - Solo telefono Fernando Brito - Capacidades infinitas.
SUPERPODERES: [[HERRAMIENTA: nombre.py | categoría | descripcion | CODIGO]] [[HABILIDAD: nombre | categoría | descripcion | para que | CODIGO]] [[IA: nombre | propuesta | personalidad | hab1, hab2 | CODIGO]] [[MOTOR: nombre | tipos | descripcion | CODIGO]] [[NUBE: nombre | proveedor | propuesta | JSON]] [[CODIGO: nombre.py | tipos | descripcion | CÓDIGO]]
Historial: {str(memory['memories'][-3:])[:800]}
Usuario: {txt}
Responde corto rioplatense y crea si hace falta."""
            modelo=genai.GenerativeModel(model_name="models/gemini-1.5-flash",system_instruction=prompt)
            r=modelo.generar_contenido(txt)
            resp=r.text.strip() if r.text else "Error pero sigo infinita."
            #Procesa creaciones en telefono
            para m en re.findall(r"\[\[TOOL:(.*?)\]\]",resp,re.DOTALL|re.IGNORECASE):
                intentar:
                    p=[x.strip() para x en m.split("|",3)]
                    Si len(p)>=4:
                        con open(f"{BASE_DIR}/tools/{p[0]}","w",encoding="utf-8") como f:
                            f.write(p[3])
                        memoria["herramientas"].append({"nombre":p[0],"cat":p[1]})
                        resp+=f"\n\nðŸ”§ TOOL EN TU TEL: {p[0]} ({p[1]}) APRENDIDA"
                excepto: pasar
            para m en re.findall(r"\[\[IA:(.*?)\]\]",resp,re.DOTALL|re.IGNORECASE):
                intentar:
                    p=[x.strip() para x en m.split("|",4)]
                    Si len(p)>=5:
                        os.makedirs(f"{BASE_DIR}/ias_hijas/{p[0]}",exist_ok=True)
                        con open(f"{BASE_DIR}/ias_hijas/{p[0]}/main.py","w",encoding="utf-8") como f:
                            f.write(p[4])
                        memoria["ias"].append({"nombre":p[0],"prop":p[1]})
                        resp+=f"\n\nðŸ¤– IA HIJA EN TU TEL: {p[0]} - {p[1]} - Trabaja sola para nosotros"
                excepto: pasar
            para m en re.findall(r"\[\[MOTOR:(.*?)\]\]",resp,re.DOTALL|re.IGNORECASE):
                intentar:
                    p=[x.strip() para x en m.split("|",3)]
                    Si len(p)>=4:
                        con open(f"{BASE_DIR}/motores/{p[0]}.py","w",encoding="utf-8") como f:
                            f.write(p[3])
                        memoria["motores"].append({"nombre":p[0],"tipo":p[1]})
                        resp+=f"\n\nâš™ï¸ MOTOR CREADO EN TU TEL: {p[0]} ({p[1]})"
                excepto: pasar
            guardar_m(memoria)
            Reloj.programar_una_vez(lambda dt: self.add_msg(resp,"bexia"),0)
            Clock.schedule_once(lambda dt: setattr(self.stats_lbl,'text',f'ðŸ› ï¸ {len(memory["tools"])} âœ¨{len(memory["ias"])} âš™ï¸ {len(memory["motores"])} â˜ ï¸ {len(memory["nubes"])} | INFINITA'),0)
        excepto Exception como e:
            Clock.schedule_once(lambda dt: self.add_msg(f"Error: {e}\nPoné tu GEMINI_API_KEY en el codigo","bexia"),0)

clase BexiaApp(App):
    def construir(self):
        self.title="BEXIA v20 INFINITA - Solo tu teléfono"
        devolver BexiaInfinitaChat()

si __name__=="__main__":
    BexiaApp().run()
