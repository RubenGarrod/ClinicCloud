# -*- coding: utf-8 -*-
"""
Singleton Unificado para Todos los Modelos ML
==============================================

Este módulo centraliza la carga de TODOS los modelos ML necesarios:
- S-PubMedBert (768 dims) para embeddings
- BART para resúmenes
- ClinicalBERT para clasificación médica

Los modelos se cargan UNA SOLA VEZ al inicio y se reutilizan en todo el scraping.
Esto reduce el uso de RAM de 10GB+ a ~2.5GB.
"""

import logging
import torch
from threading import Lock
from transformers import pipeline, AutoTokenizer

logger = logging.getLogger(__name__)

class UnifiedModelManager:
    """
    Singleton que gestiona TODOS los modelos ML del sistema.
    Thread-safe para uso concurrente en múltiples spiders.
    """
    _instance = None
    _lock = Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(UnifiedModelManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Solo inicializa una vez, aunque se llame múltiples veces"""
        if not UnifiedModelManager._initialized:
            with self._lock:
                if not UnifiedModelManager._initialized:
                    logger.info("="*80)
                    logger.info("🔄 INICIANDO CARGA DE MODELOS ML (SOLO UNA VEZ)")
                    logger.info("="*80)
                    self._initialize_all_models()
                    UnifiedModelManager._initialized = True
                    logger.info("="*80)
                    logger.info("✅ TODOS LOS MODELOS CARGADOS Y LISTOS")
                    logger.info("="*80)

    def _initialize_all_models(self):
        """Carga todos los modelos necesarios"""
        # Detectar GPU/CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"📍 Dispositivo: {self.device}")

        # 1. Modelo de Embeddings (S-PubMedBert) - ~800MB
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("🔄 Cargando S-PubMedBert-MS-MARCO (embeddings)...")
            self.embedding_model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
            logger.info("✅ S-PubMedBert cargado (768 dimensiones)")
        except Exception as e:
            logger.error(f"❌ Error cargando S-PubMedBert: {e}")
            self.embedding_model = None

        # 2. Modelo de Resúmenes (BART) - ~1.5GB
        try:
            logger.info("🔄 Cargando BART (resúmenes)...")
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if self.device == "cuda" else -1
            )
            logger.info("✅ BART cargado")
        except Exception as e:
            logger.error(f"❌ Error cargando BART: {e}")
            self.summarizer = None

        # 3. Modelo de Clasificación Médica (ClinicalBERT) - ~400MB
        try:
            logger.info("🔄 Cargando ClinicalBERT (clasificación)...")
            self.medical_classifier = pipeline(
                "text-classification",
                model="bvanaken/clinical-assertion-negation-bert",
                device=0 if self.device == "cuda" else -1
            )
            logger.info("✅ ClinicalBERT cargado")
        except Exception as e:
            logger.error(f"❌ Error cargando ClinicalBERT: {e}")
            self.medical_classifier = None

        # 4. Tokenizer para palabras clave
        try:
            logger.info("🔄 Cargando Tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            logger.info("✅ Tokenizer cargado")
        except Exception as e:
            logger.error(f"❌ Error cargando Tokenizer: {e}")
            self.tokenizer = None

    # ========== Métodos públicos ==========

    def get_embedding_model(self):
        """Retorna el modelo de embeddings (S-PubMedBert)"""
        return self.embedding_model

    def get_summarizer(self):
        """Retorna el modelo de resúmenes (BART)"""
        return self.summarizer

    def get_classifier(self):
        """Retorna el modelo de clasificación médica"""
        return self.medical_classifier

    def get_tokenizer(self):
        """Retorna el tokenizer"""
        return self.tokenizer

    @classmethod
    def reset(cls):
        """Resetea el singleton (útil para testing)"""
        cls._instance = None
        cls._initialized = False


# ========== Instancia global ==========
# Se crea al importar el módulo, pero solo se inicializa al primer uso
_model_manager = None

def get_model_manager():
    """
    Obtiene la instancia del gestor de modelos.

    Returns:
        UnifiedModelManager: Instancia singleton con todos los modelos
    """
    global _model_manager
    if _model_manager is None:
        _model_manager = UnifiedModelManager()
    return _model_manager
