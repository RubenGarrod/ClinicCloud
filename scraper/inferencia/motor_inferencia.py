import os
import logging
from typing import Dict, Any, Optional, List, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from threading import Lock
import re

# Configuración de logging
logger = logging.getLogger('inference_engine')
logger.setLevel(logging.INFO)

# Singleton para modelos
class ModelManager:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelManager, cls).__new__(cls)
                cls._instance._initialize_models()
            return cls._instance
    
    def _initialize_models(self):
        """Inicializa los modelos una sola vez"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Usando dispositivo: {self.device}")
        
        # Modelo para resúmenes cortos
        try:
            self.summarizer = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn", 
                device=0 if self.device == "cuda" else -1
            )
            logger.info("Modelo de resumen cargado correctamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo de resumen: {e}")
            self.summarizer = None
        
        # Modelo para clasificación médica (opcional)
        try:
            self.medical_classifier = pipeline(
                "text-classification", 
                model="bvanaken/clinical-assertion-negation-bert", 
                device=0 if self.device == "cuda" else -1
            )
            logger.info("Modelo de clasificación médica cargado correctamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo de clasificación médica: {e}")
            self.medical_classifier = None
        
        # Modelo para extracción de palabras clave
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            self.keyword_extractor = None  # Se implementará usando frecuencia de términos
            logger.info("Tokenizer para extracción de palabras clave cargado")
        except Exception as e:
            logger.error(f"Error al cargar el tokenizer para palabras clave: {e}")
            self.tokenizer = None


def generar_miniresumen(texto: str, max_length: int = 150, min_length: int = 50) -> str:
    """Genera un miniresumen condensado del texto.
    
    Args:
        texto: Texto a resumir
        max_length: Longitud máxima del resumen en tokens
        min_length: Longitud mínima del resumen en tokens
        
    Returns:
        Texto resumido
    """
    if not texto or not texto.strip():
        return ""
    
    try:
        # Obtener singleton del gestor de modelos
        model_manager = ModelManager()
        
        # Preprocesamiento del texto
        texto_limpio = _preprocesar_texto(texto)
        
        # Generar resumen
        if model_manager.summarizer:
            resumen = model_manager.summarizer(
                texto_limpio, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False
            )
            resumen_texto = resumen[0]['summary_text']
            
            # Aplicar postprocesamiento
            resumen_final = _postprocesar_texto(resumen_texto)
            return resumen_final
        else:
            logger.warning("Modelo de resumen no disponible, devolviendo fragmento del texto original")
            return texto[:min_length]
    except Exception as e:
        logger.error(f"Error generando resumen: {e}")
        # Fallback: devolver las primeras frases
        return texto[:min_length] if texto else ""


def clasificar_contenido_medico(texto: str) -> Dict[str, float]:
    """Clasifica el contenido médico para determinar afirmaciones, negaciones, etc.
    
    Args:
        texto: Texto médico a clasificar
        
    Returns:
        Diccionario con las categorías y sus probabilidades
    """
    if not texto or not texto.strip():
        return {"no_text": 1.0}
    
    try:
        model_manager = ModelManager()
        if model_manager.medical_classifier:
            resultado = model_manager.medical_classifier(texto[:512])  # Limitamos a 512 tokens
            return {item['label']: item['score'] for item in resultado}
        else:
            logger.warning("Modelo de clasificación médica no disponible")
            return {"unknown": 1.0}
    except Exception as e:
        logger.error(f"Error en clasificación médica: {e}")
        return {"error": 1.0}


def extraer_palabras_clave(texto: str, num_palabras: int = 5) -> List[str]:
    """Extrae las palabras clave más relevantes del texto.
    
    Args:
        texto: Texto del que extraer palabras clave
        num_palabras: Número de palabras clave a extraer
        
    Returns:
        Lista de palabras clave
    """
    if not texto or not texto.strip():
        return []
    
    try:
        model_manager = ModelManager()
        if not model_manager.tokenizer:
            return []
        
        # Lista de stopwords en inglés y español
        stopwords = set([
            "the", "and", "a", "in", "to", "of", "is", "it", "that", "for", "on",
            "with", "as", "at", "by", "from", "or", "this", "be", "are", "was",
            "el", "la", "los", "las", "un", "una", "y", "en", "de", "que", "es",
            "por", "para"
        ])
        
        # Tokenizar y limpiar
        tokens = model_manager.tokenizer.tokenize(texto.lower())
        tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
        
        # Contar frecuencias
        freq = {}
        for token in tokens:
            if token in freq:
                freq[token] += 1
            else:
                freq[token] = 1
        
        # Ordenar por frecuencia
        palabras_clave = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:num_palabras]
        return [palabra for palabra, _ in palabras_clave]
    except Exception as e:
        logger.error(f"Error extrayendo palabras clave: {e}")
        return []


def generar_analisis_completo(texto: str) -> Dict[str, Any]:
    """Genera un análisis completo del texto médico.
    
    Args:
        texto: Texto médico a analizar
        
    Returns:
        Diccionario con el análisis completo
    """
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
    
    # Eliminar múltiples espacios en blanco
    texto = re.sub(r'\s+', ' ', texto)
    
    # Eliminar caracteres especiales problemáticos
    texto = re.sub(r'[^\w\s.,;:?!-]', '', texto)
    
    return texto.strip()


def _postprocesar_texto(texto: str) -> str:
    """Mejora la calidad del resumen generado"""
    if not texto:
        return ""
    
    # Asegurar que termina con un punto
    if texto and texto[-1] not in ['.', '!', '?']:
        texto += '.'
    
    # Capitalizar primera letra
    if texto:
        texto = texto[0].upper() + texto[1:]
    
    return texto