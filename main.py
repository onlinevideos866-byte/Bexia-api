"""
BEXIA - Versión definitiva integrada
- Clima real (Open-Meteo)
- Búsqueda web real (Wikipedia + Google/DuckDuckGo), con orden ADAPTATIVO
  según qué motor viene funcionando mejor
- Base de conocimiento offline
- Memoria persistente por usuario (sobrevive reinicios)
- Aprendizaje supervisado: cola de pendientes -> propuesta -> aprobación manual
- Auto-ajuste seguro: reordena prioridades y mide su propia efectividad,
  SIN generar ni ejecutar código nuevo
"""
import os, json, re, time, uuid
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import urllib.request, urllib.parse

try:
    import requests
    HAS_REQUESTS = True
except Exception:
    HAS_REQUESTS = False

print("🌿 BEXIA iniciando...", flush=True)

OWNER_SECRET = "CAMBIA_ESTA_CLAVE_2026"  # <-- cambiá esto por tu propia clave secreta
app = FastAPI(title="BEXIA", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ============================================================
# UTILIDADES DE ARCHIVO
# ============================================================
