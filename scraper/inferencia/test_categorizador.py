# Guardar como test_categorizador.py en el directorio del proyecto

import logging
import sys
from categorizador import obtener_mejor_categoria, obtener_categorias_recomendadas, MedicalCategorizer

# Configurar logging detallado
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger('test_categorizacion')

def probar_categorizacion(titulo, abstract, nombre_prueba):
    """Prueba la categorización de un artículo específico y muestra resultados detallados"""
    print(f"\n=== PRUEBA DE {nombre_prueba} ===")
    print(f"Título: {titulo}")
    print(f"Abstract: {abstract[:100]}...")
    
    # Obtener categorización directamente del categorizador
    categorizer = MedicalCategorizer()
    categorias = categorizer.categorizar_texto(titulo, abstract)
    print(f"Categorías asignadas:")
    for cat, score in categorias:
        print(f"  - {cat}: {score:.4f} ({score*100:.1f}%)")
    
    # Obtener la mejor categoría
    mejor_cat = obtener_mejor_categoria(titulo, abstract)
    print(f"Mejor categoría: {mejor_cat}")
    
    # Categorías recomendadas
    recomendadas = obtener_categorias_recomendadas(titulo, abstract, 3)
    print(f"Categorías recomendadas: {', '.join(recomendadas)}")

# Artículos de prueba para diferentes especialidades
casos_prueba = [
    {
        "titulo": "Advances in Alzheimer's Disease Treatment: Current Clinical Trials and Novel Therapies",
        "abstract": """
        Recent advances in understanding the pathophysiology of Alzheimer's disease have led to novel therapeutic approaches. 
        This review discusses ongoing clinical trials targeting amyloid-beta, tau pathology, and neuroinflammation. 
        We also examine emerging biomarkers for early diagnosis and treatment response monitoring in the brain.
        """,
        "nombre": "NEUROLOGÍA"
    },
    {
        "titulo": "Novel Anticoagulation Strategies in Atrial Fibrillation Management",
        "abstract": """
        Atrial fibrillation remains a significant risk factor for stroke. This paper reviews current anticoagulation 
        therapies and emerging approaches. We examine direct oral anticoagulants compared to traditional warfarin therapy,
        focusing on efficacy, safety profiles, and adherence in patients with cardiovascular conditions.
        """,
        "nombre": "CARDIOLOGÍA"
    },
    {
        "titulo": "Biologics in Psoriasis Treatment: Long-term Efficacy and Safety",
        "abstract": """
        This study evaluates long-term outcomes of biologic therapies for moderate to severe psoriasis. 
        We analyze data from 5-year follow-up studies on TNF-alpha inhibitors, IL-17 inhibitors, and IL-23 blockers,
        measuring PASI scores, adverse events, and patient-reported quality of life metrics related to skin conditions.
        """,
        "nombre": "DERMATOLOGÍA"
    },
    {
        "titulo": "Advances in Type 2 Diabetes Management: New Insulin Formulations",
        "abstract": """
        This review examines recent developments in insulin therapy for type 2 diabetes mellitus. We discuss 
        ultra-long-acting insulin analogs, smart insulin delivery systems, and combination therapies with GLP-1 
        receptor agonists. The article highlights improvements in glycemic control, reduced hypoglycemia risk, 
        and quality of life outcomes in patients with diabetes.
        """,
        "nombre": "ENDOCRINOLOGÍA"
    },
    {
        "titulo": "Novel Approaches in Asthma Treatment: Biologics and Bronchial Thermoplasty",
        "abstract": """
        This article reviews emerging therapies for severe asthma, focusing on monoclonal antibodies targeting 
        type 2 inflammation pathways and bronchial thermoplasty. We analyze efficacy data from recent clinical trials, 
        examining reductions in exacerbation rates, improvements in lung function, and changes in quality of life 
        measures in patients with treatment-resistant asthma.
        """,
        "nombre": "NEUMOLOGÍA"
    }
]

# Ejecutar todas las pruebas
for caso in casos_prueba:
    probar_categorizacion(caso["titulo"], caso["abstract"], caso["nombre"])

print("\nPruebas de categorización completadas.")