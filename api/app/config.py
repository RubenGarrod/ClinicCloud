# -*- coding: utf-8 -*-
"""
Script de configuracion de la API REST de ClinicCloud.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
# IMPORTANTE: DATABASE_URL debe configurarse en .env - no hay default seguro
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cliniccloud:changeme@db:5432/cliniccloud")

# Configuración del motor de búsqueda
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "20"))