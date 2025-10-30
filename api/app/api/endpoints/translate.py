# -*- coding: utf-8 -*-
"""
Endpoint para traducir texto utilizando la API de Microsoft Translator.
"""
import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter()

# Carga variables de entorno
TRANSLATOR_KEY = os.getenv("TRANSLATOR_API_KEY")
TRANSLATOR_REGION = os.getenv("TRANSLATOR_REGION", "westeurope")
TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"

# Validación de la entrada
class TranslationRequest(BaseModel):
    text: str
    to: str
    from_lang: str = None  # opcional

@router.post("/translate")
async def translate_text(request: TranslationRequest):
    # Si no hay clave de API configurada, usar un fallback simple
    if not TRANSLATOR_KEY:
        # Implementación de fallback muy básica para desarrollo
        return {"translatedText": request.text}  # Devuelve el texto original sin traducir

    params = {
        "api-version": "3.0",
        "to": request.to,
    }
    if request.from_lang:
        params["from"] = request.from_lang

    headers = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": TRANSLATOR_REGION,
        "Content-type": "application/json",
    }

    body = [{"text": request.text}]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TRANSLATOR_ENDPOINT}/translate",
                params=params,
                headers=headers,
                json=body,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return {"translatedText": data[0]["translations"][0]["text"]}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al traducir: {str(e)}")