# -*- coding: utf-8 -*-
"""
Modulo de inferencia para análisis de texto médico.
Este módulo utiliza modelos de aprendizaje para realizar tareas como
resumen, clasificación y extracción de palabras clave en textos médicos.

OPTIMIZACIÓN: Ahora usa UnifiedModelManager que carga TODOS los modelos
una sola vez al inicio, compartidos entre todos los procesos.
"""
import os
import logging
from typing import Dict, Any, Optional, List, Tuple
import re

logger = logging.getLogger('inference_engine')
logger.setLevel(logging.INFO)

# =====================================================
# USAR SINGLETON UNIFICADO
# =====================================================
# Importamos el gestor unificado que carga todos los modelos UNA SOLA VEZ
from .model_singletons import get_model_manager

# Mantener ModelManager para compatibilidad con código existente
# pero ahora solo es un wrapper del UnifiedModelManager
def ModelManager():
    """
    Wrapper para compatibilidad con código existente.
    Retorna la instancia del UnifiedModelManager.
    """
    return get_model_manager()


def generar_miniresumen(texto: str, max_length: int = 150, min_length: int = 50) -> str:
    """Genera un resumen condensado del texto."""
    if not texto or not texto.strip():
        return ""
    
    try:
        # se inicializa con el singleton del gestor de modelos
        # para evitar cargar el modelo cada vez que se llama a la función
        model_manager = ModelManager()
        
        #preprocesamos el texto para normalizarlo
        # y eliminar caracteres no deseados
        texto_limpio = _preprocesar_texto(texto)
        
        # se genera el resumen con el modelo de BART
        # max_length y min_length son los límites de longitud del resumen
        if model_manager.summarizer:
            resumen = model_manager.summarizer(
                texto_limpio, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False
            )
            resumen_texto = resumen[0]['summary_text']

            # postprocesar el resumen para mejorar la calidad
            resumen_final = _postprocesar_texto(resumen_texto)
            return resumen_final
        else:
            logger.warning("Modelo de resumen no disponible, devolviendo fragmento del texto original")
            return texto[:min_length]
    except Exception as e:
        logger.error(f"Error generando resumen: {e}")
        # como fallback: se devuelven los primeros caracteres del texto original (la longitud minima)
        # o una cadena vacía si el texto está vacío
        return texto[:min_length] if texto else ""


def clasificar_contenido_medico(texto: str) -> Dict[str, float]:
    """Clasifica el contenido médico del texto."""
    # si el texto está vacío o solo tiene espacios, devolvemos un diccionario con una clave "no_text"
    if not texto or not texto.strip():
        return {"no_text": 1.0}
    
    try:
        model_manager = ModelManager()
        if model_manager.medical_classifier:
            resultado = model_manager.medical_classifier(texto[:512])  
            return {item['label']: item['score'] for item in resultado}
        else:
            logger.warning("Modelo de clasificación médica no disponible")
            return {"unknown": 1.0}
    except Exception as e:
        logger.error(f"Error en clasificación médica: {e}")
        return {"error": 1.0}


def extraer_palabras_clave(texto: str, num_palabras: int = 5) -> List[str]:
    """Extrae las palabras clave más relevantes del texto."""
    if not texto or not texto.strip():
        return []
    try:
        model_manager = ModelManager()
        if not model_manager.tokenizer:
            return []
        # stopwords en inglés y español
        stopwords = set([
            "the", "and", "a", "in", "to", "of", "is", "it", "that", "for", "on",
            "with", "as", "at", "by", "from", "or", "this", "be", "are", "was",
            "el", "la", "los", "las", "un", "una", "y", "en", "de", "que", "es",
            "por", "para"
        ])
        
        # tokenizacion y limpieza
        tokens = model_manager.tokenizer.tokenize(texto.lower())
        tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
        
        # cont frecuencias de los tokens
        freq = {}
        for token in tokens:
            if token in freq:
                freq[token] += 1
            else:
                freq[token] = 1
        
        # y ordenamos por frecuencia
        palabras_clave = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:num_palabras]
        return [palabra for palabra, _ in palabras_clave]
    except Exception as e:
        logger.error(f"Error extrayendo palabras clave: {e}")
        return []


def generar_analisis_completo(texto: str) -> Dict[str, Any]:
    """Genera un análisis completo del texto médico."""
    resultado = {
        "resumen": generar_miniresumen(texto),
        "clasificacion": clasificar_contenido_medico(texto),
        "palabras_clave": extraer_palabras_clave(texto),
        "longitud_original": len(texto) if texto else 0
    }
    
    return resultado


def _preprocesar_texto(texto: str) -> str:
    """Preprocesa el texto para mejorar la calidad del resumen"""
    if not texto:
        return ""
    
    # borrar espacios en blanco (mas de 1) y caracteres problematicos
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s.,;:?!-]', '', texto)
    
    return texto.strip()


def _postprocesar_texto(texto: str) -> str:
    """Mejora la calidad del resumen generado"""
    if not texto:
        return ""
    
    # que termine con un punto
    if texto and texto[-1] not in ['.', '!', '?']:
        texto += '.'
    
    # primera letra en mayús
    if texto:
        texto = texto[0].upper() + texto[1:]
    
    return texto