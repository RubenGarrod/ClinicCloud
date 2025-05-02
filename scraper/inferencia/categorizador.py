import logging
from typing import Dict, List, Tuple, Optional
import re
import torch
from threading import Lock

# Configuración de logging
logger = logging.getLogger('medical_categorization')
logger.setLevel(logging.INFO)

# Definición de categorías médicas - revisada y mejorada
CATEGORIAS_MEDICAS = {
    "Oncología": ["cancer", "tumor", "oncolog", "metasta", "carcinom", "leukemi", "lymphom", "neoplasm", "melanoma", "sarcoma", "chemotherapy", "radiotherapy"],
    
    "Cardiología": ["heart", "cardi", "cardiovascular", "coronary", "arterial", "myocardial", "aorta", "hypertension", "atherosclerosis", "thrombosis", "stent", "arrhythmia", "atrial", "ventricular", "angina"],
    
    "Neurología": ["brain", "neuro", "nerve", "cerebral", "cognitive", "alzheimer", "parkinson", "epilepsy", "seizure", "dementia", "multiple sclerosis", "stroke", "migraine", "neuropathy"],
    
    "Endocrinología": ["hormone", "diabetes", "thyroid", "insulin", "endocrin", "metabolic", "gland", "obesity", "pituitary", "adrenal", "pancreas", "glucose"],
    
    "Gastroenterología": ["stomach", "intestine", "digestive", "liver", "bowel", "colon", "hepatic", "gastric", "ulcer", "crohn", "colitis", "pancreatitis", "celiac", "cirrhosis"],
    
    "Neumología": ["lung", "respiratory", "pulmonary", "asthma", "bronch", "pneumonia", "copd", "tuberculosis", "emphysema", "pleural", "airway", "ventilation"],
    
    "Nefrología": ["kidney", "renal", "nephro", "dialysis", "urinary", "bladder", "nephritis", "glomerular", "transplant", "proteinuria"],
    
    "Infectología": ["infection", "bacteria", "virus", "antibiotic", "pathogen", "microbial", "sepsis", "fungal", "parasitic", "antimicrobial", "resistance", "hiv", "aids"],
    
    "Inmunología": ["immune", "antibody", "allergy", "autoimmune", "immunodeficiency", "transplant", "rejection", "antigen", "cytokine", "inflammation", "vaccine"],
    
    "Hematología": ["blood", "anemia", "clot", "thrombosis", "hemophilia", "leukocyte", "platelet", "transfusion", "coagulation", "marrow", "erythrocyte"],
    
    "Dermatología": ["skin", "derma", "rash", "acne", "psoriasis", "eczema", "dermatitis", "pigmentation", "melanoma", "lesion", "wound"],
    
    "Pediatría": ["child", "infant", "pediatric", "neonatal", "adolescent", "birth", "congenital", "growth", "developmental", "newborn"],
    
    "Geriatría": ["elderly", "aging", "geriatric", "old age", "frailty", "dementia", "longevity", "senior", "gerontology"],
    
    "Obstetricia y Ginecología": ["pregnancy", "gynecol", "obstetric", "menopause", "fertility", "uterus", "ovarian", "cervical", "contraception", "menstrual", "prenatal", "birth"],
    
    "Reumatología": ["arthritis", "rheumatic", "autoimmune", "joint", "rheumatoid", "lupus", "inflammation", "gout", "fibromyalgia", "spondylitis"],
    
    "Oftalmología": ["eye", "vision", "ophthalm", "retina", "cataract", "glaucoma", "cornea", "ocular", "blind", "macular"],
    
    "Otorrinolaringología": ["ear", "nose", "throat", "hearing", "auditory", "nasal", "laryngeal", "tonsil", "sinus", "otitis"],
    
    "Psiquiatría": ["mental", "psychiatric", "depression", "anxiety", "schizophrenia", "bipolar", "disorder", "cognitive", "addiction", "psycho", "therapy"],
    
    "Traumatología": ["bone", "trauma", "orthopedic", "fracture", "joint", "ligament", "muscle", "tendon", "spine", "surgery", "rehabilitation"],
    
    "Urología": ["urinary", "prostate", "urology", "bladder", "kidney", "testicular", "urological", "erectile", "urinary tract"],
    
    "Genética Médica": ["gene", "genetic", "dna", "chromosome", "hereditary", "mutation", "genomic", "inheritance", "sequence", "molecular"]
}

# Términos generales de medicina (no específicos a una categoría)
TERMINOS_GENERALES = ["medicine", "treatment", "patient", "therapy", "clinical", "medical", "health", "disease", "symptom", "diagnosis", "care", "physician", "doctor", "healthcare", "trial"]

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
        
        # NO usaremos el modelo preentrenado ya que no está funcionando correctamente
        self.use_model = False
        logger.info("Usando sistema basado en reglas para la categorización")
    
    def categorizar_texto(self, titulo: str, abstract: str) -> List[Tuple[str, float]]:
        """ Categoriza un texto médico basado en su título y resumen"""
        # Concatenar título y resumen, dando más peso al título
        texto_completo = f"{titulo} {titulo} {abstract}"
        texto_completo = texto_completo.lower()
        
        # Solo usamos el método basado en reglas mejorado
        return self._categorizar_con_reglas_mejorado(texto_completo)
    
    def _categorizar_con_reglas_mejorado(self, texto: str) -> List[Tuple[str, float]]:
        """Categoriza usando un sistema de reglas mejorado"""
        resultados = []
        puntuaciones = {categoria: 0.0 for categoria in CATEGORIAS_MEDICAS}
        
        # Normalizar el texto (convertir a minúsculas)
        texto = texto.lower()
        
        # Contar ocurrencias de términos clave para cada categoría
        for categoria, terminos in CATEGORIAS_MEDICAS.items():
            logger.debug(f"Analizando categoría: {categoria}")
            
            for termino in terminos:
                # Buscar el término como palabra completa o parte de palabra
                patron = r'\b' + re.escape(termino) + r'[a-z]*\b'
                ocurrencias = len(re.findall(patron, texto, re.IGNORECASE))
                
                if ocurrencias > 0:
                    logger.debug(f"  Término '{termino}' encontrado {ocurrencias} veces")
                    # Ponderación basada en la especificidad del término
                    especificidad = 1.0
                    # Los términos más largos suelen ser más específicos
                    if len(termino) > 6:
                        especificidad = 1.5
                    puntuaciones[categoria] += ocurrencias * especificidad
        
        # Penalizar categorías por términos generales
        total_generales = 0
        for termino in TERMINOS_GENERALES:
            patron = r'\b' + re.escape(termino) + r'[a-z]*\b'
            ocurrencias_gen = len(re.findall(patron, texto, re.IGNORECASE))
            total_generales += ocurrencias_gen
        
        # Si hay muchos términos generales pero pocas coincidencias específicas
        # significa que probablemente es un texto médico general
        if total_generales > 10:
            puntuaciones["Medicina General"] = total_generales * 0.2
            
            # Si no hay puntuaciones significativas en otras categorías
            if all(puntuacion < 2.0 for puntuacion in puntuaciones.values()):
                puntuaciones["Medicina General"] += 5.0  # Dar más peso a Medicina General
        
        # Buscar términos específicos en el título para dar prioridad
        titulo_peso = 3.0  # Factor de peso para coincidencias en el título
        
        # Depuración de puntuaciones
        logger.debug("Puntuaciones por categoría:")
        for cat, punt in sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True):
            if punt > 0:
                logger.debug(f"  {cat}: {punt}")
        
        # Convertir a lista de tuplas y normalizar
        total_puntuacion = sum(puntuaciones.values())
        if total_puntuacion > 0:
            for categoria, puntuacion in puntuaciones.items():
                if puntuacion > 0:
                    # Normalizar para que sumen 1.0
                    puntuacion_normalizada = puntuacion / total_puntuacion
                    resultados.append((categoria, puntuacion_normalizada))
        else:
            return [("Medicina General", 1.0)]
        
        # Ordenar por puntuación y devolver las mejores
        resultados = sorted(resultados, key=lambda x: x[1], reverse=True)
        return resultados[:3] if resultados else [("Medicina General", 1.0)]


def obtener_mejor_categoria(titulo: str, abstract: str) -> str:
    """Obtiene la mejor categoría para un documento médico"""
    try:
        categorizer = MedicalCategorizer()
        categorias = categorizer.categorizar_texto(titulo, abstract)
        
        # Imprimir más información de debug
        logger.debug(f"Título: {titulo[:50]}...")
        logger.debug(f"Abstract: {abstract[:50]}...")
        logger.debug(f"Categorías asignadas: {categorias}")
        
        if categorias:
            mejor_categoria = categorias[0][0]
            logger.debug(f"Mejor categoría seleccionada: {mejor_categoria}")
            return mejor_categoria
        else:
            logger.warning("No se encontraron categorías - usando Medicina General")
            return "Medicina General"
    except Exception as e:
        logger.error(f"Error al categorizar documento: {e}")
        return "Medicina General"


def obtener_categorias_recomendadas(titulo: str, abstract: str, n: int = 3) -> List[str]:
    """Obtiene las n mejores categorías recomendadas para un documento """
    try:
        categorizer = MedicalCategorizer()
        categorias = categorizer.categorizar_texto(titulo, abstract)
        
        logger.debug(f"Categorías recomendadas: {categorias[:n]}")
        return [cat[0] for cat in categorias[:n]]
    except Exception as e:
        logger.error(f"Error al obtener categorías recomendadas: {e}")
        return ["Medicina General"]