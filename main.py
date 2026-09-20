"""
BEXIA - Módulo de aprendizaje supervisado
==========================================
Flujo:
  1. Cuando Bexia no puede responder algo bien, lo anota en una cola
     (bexia_pendientes.json) en vez de inventar una respuesta.
  2. Vos (el dueño, con OWNER_SECRET) consultás esa cola desde un
     endpoint protegido.
  3. Para cada pendiente, Bexia puede PROPONER una entrada de
     conocimiento o una función nueva — como texto, nunca como código
     que se ejecuta sola.
  4. Vos revisás la propuesta y, si te gusta, la aprobás con otro
     endpoint protegido. Recién ahí se guarda en disco y queda activa.

Nada de esto ejecuta código generado automáticamente. Todo pasa por
tu aprobación explícita.
"""
import uuid

# ============================================================
# 1. COLA DE PREGUNTAS SIN RESPUESTA
# ============================================================
ARCHIVO_PENDIENTES = "bexia_pendientes.json"
pendientes = load_json(ARCHIVO_PENDIENTES, {})  # {id: {...}}

def guardar_pendientes():
    save_json(ARCHIVO_PENDIENTES, pendientes)

def registrar_pendiente(pregunta_original, motivo="sin_respuesta_web"):
    """Se llama desde cerebro() cuando ni la base offline ni la búsqueda
    web dieron una respuesta útil."""
    pid = uuid.uuid4().hex[:8]
    pendientes[pid] = {
        "pregunta": pregunta_original,
