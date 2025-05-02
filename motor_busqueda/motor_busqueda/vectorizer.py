import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

class TextVectorizer:
    """Clase para transformar texto a embeddings vectoriales"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Inicializa el vectorizador con el modelo especificado"""
        self.logger = logging.getLogger('vectorizer')
        try:
            self.model = SentenceTransformer(model_name)
            self.logger.info(f"Modelo {model_name} cargado correctamente")
        except Exception as e:
            self.logger.error(f"Error al cargar el modelo: {e}")
            # Modo de fallback (no óptimo pero permite operar)
            self.model = None
            
    def encode(self, text: str) -> List[float]:
        """Convierte texto a vector de embeddings"""
        if not text:
            return self._generate_empty_vector()
            
        try:
            if self.model:
                # Usar el modelo para generar el embedding
                vector = self.model.encode(text)
                
                # Asegurar que el vector tiene la dimensión correcta (768)
                padded_vector = np.zeros(768)
                padded_vector[:min(len(vector), 768)] = vector[:min(len(vector), 768)]
                
                return padded_vector.tolist()
            else:
                self.logger.warning("Modelo no disponible, generando vector aleatorio")
                return self._generate_empty_vector()
                
        except Exception as e:
            self.logger.error(f"Error al vectorizar texto: {e}")
            return self._generate_empty_vector()
    
    def _generate_empty_vector(self) -> List[float]:
        """Genera un vector vacío (zeros) como fallback"""
        return [0.0] * 768  # Dimensión del vector de embeddings