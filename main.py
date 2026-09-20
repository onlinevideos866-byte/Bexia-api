"""
BEXIA - Versión integrada
- Clima real (Open-Meteo)
- Búsqueda web real (Wikipedia + Google/DuckDuckGo)
- Base de conocimiento offline
- Memoria persistente por usuario (sobrevive reinicios)
- Aprendizaje supervisado: cola de pendientes -> propuesta -> aprobación manual
"""
import os, json, re, time, random, uuid
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

OWNER_SECRET = "BEXIA_FER_2026_INFINITA_SUPREMA"  # cambialo por tu propia clave
app = FastAPI(title="BEXIA", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ============================================================
# UTILIDADES DE ARCHIVO
# ============================================================
def load_json(p, d):
    try:
        if os.path.exists(p):
