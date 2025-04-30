import logging
from typing import Dict, List, Tuple, Optional
import re
import torch # type: ignore
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from threading import Lock

# Configuración de logging
logger = logging.getLogger('medical_categorization')
logger.setLevel(logging.INFO)

# Definición de categorías médicas
CATEGORIAS_MEDICAS = {
    "Oncología": ["cancer", "tumor", "oncolog", "metasta", "carcinom", "leukemi", "lymphom", "neoplasm"],
    "Cardiología": ["heart", "cardio", "cardiac", "cardiovascular", "coronary", "arterial", "myocardial", "aorta"],
    "Neurología": ["brain", "neuro", "nerve", "cerebral", "cognitive", "alzheimer", "parkinson", "epilepsy"],
    "Endocrinología": ["hormone", "diabetes", "thyroid", "insulin", "endocrin", "metabolic", "gland", "obesity"],
    "Gastroenterología": ["stomach", "intestine", "digestive", "liver", "bowel", "colon", "hepatic", "gastric"],
    "Neumología": ["lung", "respiratory", "pulmonary", "asthma", "bronch", "pneumonia", "copd", "tuberculosis"],
    "Nefrología": ["kidney", "renal", "nephro", "dialysis", "urinary", "bladder", "nephritis"],
    "Infectología": ["infection", "bacteria", "virus", "antibiotic", "pathogen", "microbial", "sepsis", "fungal"],
    "Inmunología": ["immune", "antibody", "allergy", "autoimmune", "immunodeficiency", "transplant", "rejection"],
    "Hematología": ["blood", "anemia", "clot", "thrombosis", "hemophilia", "leukocyte", "platelet", "transfusion"],
    "Dermatología": ["skin", "derma", "rash", "acne", "psoriasis", "eczema", "melanoma", "dermatitis"],
    "Pediatría": ["child", "infant", "pediatric", "neonatal", "adolescent", "birth", "congenital"],
    "Geriatría": ["elderly", "aging", "geriatric", "old age", "frailty", "dementia", "longevity"],
    "Obstetricia y Ginecología": ["pregnancy", "gynecology", "obstetric", "menopause", "fertility", "uterus", "ovarian"],
    "Reumatología": ["arthritis", "rheumatic", "autoimmune", "joint", "rheumatoid", "lupus", "inflammation"],
    "Oftalmología": ["eye", "vision", "ophthalm", "retina", "cataract", "glaucoma", "cornea"],
    "Otorrinolaringología": ["ear", "nose", "throat", "hearing", "auditory", "nasal", "laryngeal", "tonsil"],
    "Psiquiatría": ["mental", "psychiatric", "depression", "anxiety", "schizophrenia", "bipolar", "disorder"],
    "Traumatología": ["bone", "trauma", "orthopedic", "fracture", "joint", "ligament", "muscle", "tendon"],
    "Urología": ["urinary", "prostate", "urology", "bladder", "kidney", "testicular", "urological"],
    "Genética Médica": ["gene", "genetic", "dna", "chromosome", "hereditary", "mutation", "genomic"]
}

# Términos generales de medicina (no específicos a una categoría)
TERMINOS_GENERALES = ["medicine", "treatment", "patient", "therapy", "clinical", "medical", "health", "disease", "symptom"]

class MedicalCategorizer:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MedicalCategorizer, cls).__new__(cls)
                cls._instance._initialize_categorizer()
            return cls._instance
    
    def _initialize_categorizer(self):
        """Inicializa los componentes del categorizador"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Usando dispositivo: {self.device}")
        
        # Intentar cargar un modelo especializado para categorización médica
        try:
            model_name = "allenai/biomed_roberta_base"  # Modelo preentrenado para textos biomédicos
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.use_model = True
            logger.info(f"Modelo de categorización médica '{model_name}' cargado correctamente")
        except Exception as e:
            logger.warning(f"No se pudo cargar el modelo de categorización: {e}")
            logger.info("Se usará el método basado en reglas como fallback")
            self.use_model = False
    
    def categorizar_texto(self, titulo: str, abstract: str) -> List[Tuple[str, float]]:
        """ Categoriza un texto médico basado en su título y resumen"""
        # título y resumen combinados, dando más peso al título
        texto_completo = f"{titulo} {titulo} {abstract}"
        texto_completo = texto_completo.lower()
        
        if self.use_model:
            return self._categorizar_con_modelo(texto_completo)
        else:
            return self._categorizar_con_reglas(texto_completo)
    
    def _categorizar_con_modelo(self, texto: str) -> List[Tuple[str, float]]:
        """Categoriza usando el modelo de ML"""
        try:
            # Preparar el texto para el modelo
            inputs = self.tokenizer(texto[:512], return_tensors="pt", padding=True, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Hacer la predicción
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Convertir a probabilidades
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Mapear las categorías
            categorias = list(CATEGORIAS_MEDICAS.keys())
            resultados = [(categorias[i % len(categorias)], probs[0][i].item()) 
                          for i in range(min(len(categorias), len(probs[0])))]
            
            # Ordenar por probabilidad
            resultados = sorted(resultados, key=lambda x: x[1], reverse=True)
            return resultados[:3]  # Devolver las 3 mejores categorías
        except Exception as e:
            logger.error(f"Error en categorización con modelo: {e}")
            return self._categorizar_con_reglas(texto)
    
    def _categorizar_con_reglas(self, texto: str) -> List[Tuple[str, float]]:
        """Categoriza usando reglas basadas en palabras clave"""
        resultados = []
        puntuaciones = {categoria: 0.0 for categoria in CATEGORIAS_MEDICAS}
        
        # Contar ocurrencias de términos clave
        for categoria, terminos in CATEGORIAS_MEDICAS.items():
            for termino in terminos:
                # Buscar el término como palabra completa o parte de palabra
                ocurrencias = len(re.findall(r'\b' + termino + r'[a-z]*\b', texto, re.IGNORECASE))
                if ocurrencias > 0:
                    puntuaciones[categoria] += ocurrencias * 0.5
                    # si está en el título (puntos extra por impoirtancia)
                    if ocurrencias >= 2:
                        puntuaciones[categoria] += 0.5
        
        # Penalizar categorías basadas en términos generales
        total_generales = 0
        for termino in TERMINOS_GENERALES:
            total_generales += len(re.findall(r'\b' + termino + r'[a-z]*\b', texto, re.IGNORECASE))
        
        # Si hay muchos términos generales, esto podría ser un texto general
        if total_generales > 10:
            puntuaciones["Medicina General"] = total_generales * 0.1
        
        # Convertir a lista de tuplas
        for categoria, puntuacion in puntuaciones.items():
            if puntuacion > 0:
                puntuacion_norm = min(puntuacion / 10.0, 1.0)
                resultados.append((categoria, puntuacion_norm))
        
        # Ordenar por puntuación y devolver las 3 mejores
        resultados = sorted(resultados, key=lambda x: x[1], reverse=True)
        return resultados[:3] if resultados else [("Medicina General", 1.0)]


def obtener_mejor_categoria(titulo: str, abstract: str) -> str:
    """Obtiene la mejor categoría para un documento médico"""
    try:
        categorizer = MedicalCategorizer()
        categorias = categorizer.categorizar_texto(titulo, abstract)
        
        if categorias:
            return categorias[0][0] # la categoría con mayor puntuación
        else:
            return "Medicina General"
    except Exception as e:
        logger.error(f"Error al categorizar documento: {e}")
        return "Medicina General"


def obtener_categorias_recomendadas(titulo: str, abstract: str, n: int = 3) -> List[str]:
    """Obtiene las n mejores categorías recomendadas para un documento """
    try:
        categorizer = MedicalCategorizer()
        categorias = categorizer.categorizar_texto(titulo, abstract)
        
        return [cat[0] for cat in categorias[:n]] # las n mejores categorías
    except Exception as e:
        logger.error(f"Error al obtener categorías recomendadas: {e}")
        return ["Medicina General"]