# -*- coding: utf-8 -*-
"""
Sistema Híbrido de Categorización: MeSH Terms + Keywords
Este módulo utiliza MeSH (Medical Subject Headings) oficiales de NLM
combinados con el sistema de keywords existente para mejor precisión.
"""
import logging
from typing import List, Optional
from .categorizador import MedicalCategorizer, logger

# Mapeo de MeSH Terms a Categorías Médicas
# MeSH (Medical Subject Headings) son términos de categorización oficial de NLM
MESH_TO_CATEGORIA = {
    # Oncología
    "Neoplasms": "Oncología",
    "Carcinoma": "Oncología",
    "Cancer": "Oncología",
    "Tumor": "Oncología",
    "Lymphoma": "Oncología",
    "Leukemia": "Oncología",
    "Melanoma": "Oncología",
    "Sarcoma": "Oncología",
    "Oncology": "Oncología",

    # Cardiología
    "Heart Diseases": "Cardiología",
    "Cardiovascular Diseases": "Cardiología",
    "Coronary Disease": "Cardiología",
    "Myocardial Infarction": "Cardiología",
    "Heart Failure": "Cardiología",
    "Arrhythmias, Cardiac": "Cardiología",
    "Hypertension": "Cardiología",
    "Cardiology": "Cardiología",

    # Neurología
    "Nervous System Diseases": "Neurología",
    "Brain Diseases": "Neurología",
    "Alzheimer Disease": "Neurología",
    "Parkinson Disease": "Neurología",
    "Epilepsy": "Neurología",
    "Multiple Sclerosis": "Neurología",
    "Stroke": "Neurología",
    "Dementia": "Neurología",
    "Neurology": "Neurología",

    # Endocrinología
    "Diabetes Mellitus": "Endocrinología",
    "Diabetes Mellitus, Type 2": "Endocrinología",
    "Diabetes Mellitus, Type 1": "Endocrinología",
    "Thyroid Diseases": "Endocrinología",
    "Obesity": "Endocrinología",
    "Metabolic Diseases": "Endocrinología",
    "Endocrine System Diseases": "Endocrinología",

    # Gastroenterología
    "Gastrointestinal Diseases": "Gastroenterología",
    "Liver Diseases": "Gastroenterología",
    "Inflammatory Bowel Diseases": "Gastroenterología",
    "Crohn Disease": "Gastroenterología",
    "Colitis, Ulcerative": "Gastroenterología",
    "Cirrhosis": "Gastroenterología",

    # Neumología
    "Lung Diseases": "Neumología",
    "Respiratory Tract Diseases": "Neumología",
    "Asthma": "Neumología",
    "Pulmonary Disease, Chronic Obstructive": "Neumología",
    "Pneumonia": "Neumología",
    "Tuberculosis": "Neumología",

    # Nefrología
    "Kidney Diseases": "Nefrología",
    "Renal Insufficiency": "Nefrología",
    "Kidney Failure, Chronic": "Nefrología",
    "Nephritis": "Nefrología",

    # Infectología
    "Infection": "Infectología",
    "Bacterial Infections": "Infectología",
    "Virus Diseases": "Infectología",
    "HIV Infections": "Infectología",
    "Tuberculosis": "Infectología",
    "Sepsis": "Infectología",

    # Inmunología
    "Immune System Diseases": "Inmunología",
    "Autoimmune Diseases": "Inmunología",
    "Immunologic Deficiency Syndromes": "Inmunología",
    "Hypersensitivity": "Inmunología",

    # Hematología
    "Hematologic Diseases": "Hematología",
    "Anemia": "Hematología",
    "Leukemia": "Hematología",
    "Thrombosis": "Hematología",
    "Hemophilia": "Hematología",

    # Dermatología
    "Skin Diseases": "Dermatología",
    "Dermatitis": "Dermatología",
    "Psoriasis": "Dermatología",
    "Eczema": "Dermatología",

    # Pediatría
    "Child": "Pediatría",
    "Infant": "Pediatría",
    "Pediatrics": "Pediatría",
    "Adolescent": "Pediatría",

    # Geriatría
    "Aged": "Geriatría",
    "Aging": "Geriatría",
    "Geriatrics": "Geriatría",

    # Obstetricia y Ginecología
    "Pregnancy": "Obstetricia y Ginecología",
    "Obstetrics": "Obstetricia y Ginecología",
    "Gynecology": "Obstetricia y Ginecología",
    "Pregnancy Complications": "Obstetricia y Ginecología",
    "Genital Diseases, Female": "Obstetricia y Ginecología",

    # Reumatología
    "Rheumatic Diseases": "Reumatología",
    "Arthritis": "Reumatología",
    "Arthritis, Rheumatoid": "Reumatología",
    "Lupus Erythematosus, Systemic": "Reumatología",

    # Oftalmología
    "Eye Diseases": "Oftalmología",
    "Cataract": "Oftalmología",
    "Glaucoma": "Oftalmología",
    "Retinal Diseases": "Oftalmología",

    # Otorrinolaringología
    "Otorhinolaryngologic Diseases": "Otorrinolaringología",
    "Ear Diseases": "Otorrinolaringología",
    "Nose Diseases": "Otorrinolaringología",
    "Laryngeal Diseases": "Otorrinolaringología",

    # Psiquiatría
    "Mental Disorders": "Psiquiatría",
    "Depression": "Psiquiatría",
    "Anxiety Disorders": "Psiquiatría",
    "Schizophrenia": "Psiquiatría",
    "Bipolar Disorder": "Psiquiatría",

    # Traumatología
    "Wounds and Injuries": "Traumatología",
    "Fractures, Bone": "Traumatología",
    "Musculoskeletal Diseases": "Traumatología",
    "Orthopedics": "Traumatología",

    # Urología
    "Urologic Diseases": "Urología",
    "Prostatic Diseases": "Urología",
    "Urinary Tract Infections": "Urología",

    # Genética Médica
    "Genetic Diseases, Inborn": "Genética Médica",
    "Genetics": "Genética Médica",
    "DNA": "Genética Médica",
    "Mutation": "Genética Médica",
}


def categorizar_con_mesh(mesh_terms: List[str]) -> Optional[str]:
    """Categoriza un documento basado en sus MeSH terms oficiales de NLM"""
    if not mesh_terms:
        return None

    logger.debug(f"Analizando {len(mesh_terms)} MeSH terms")

    # Intentar match exacto primero
    for mesh_term in mesh_terms:
        if mesh_term in MESH_TO_CATEGORIA:
            categoria = MESH_TO_CATEGORIA[mesh_term]
            logger.info(f"✓ Match exacto MeSH: '{mesh_term}' → {categoria}")
            return categoria

    # Match parcial (el MeSH term contiene la keyword o viceversa)
    for mesh_term in mesh_terms:
        for mesh_key, categoria in MESH_TO_CATEGORIA.items():
            if mesh_key.lower() in mesh_term.lower() or mesh_term.lower() in mesh_key.lower():
                logger.info(f"✓ Match parcial MeSH: '{mesh_term}' ~ '{mesh_key}' → {categoria}")
                return categoria

    logger.debug("No se encontró categoría basada en MeSH terms")
    return None


def obtener_mejor_categoria_con_mesh(titulo: str, abstract: str, mesh_terms: List[str] = None) -> str:
    """
    Versión mejorada de categorización con sistema híbrido:
    1. Prioriza MeSH terms (más confiables, categorización oficial de NLM)
    2. Fallback a sistema de keywords si no hay MeSH terms
    """
    try:
        # Estrategia 1: Intentar categorizar con MeSH terms (PRIORITARIO)
        if mesh_terms and len(mesh_terms) > 0:
            categoria_mesh = categorizar_con_mesh(mesh_terms)
            if categoria_mesh:
                logger.info(f"✓ Categoría asignada por MeSH terms: {categoria_mesh}")
                return categoria_mesh

        # Estrategia 2: Fallback a sistema de keywords
        logger.info("Usando sistema de keywords (no hay MeSH terms o no coincidieron)")
        categorizer = MedicalCategorizer()
        categorias = categorizer.categorizar_texto(titulo, abstract)

        if categorias:
            mejor_categoria = categorias[0][0]
            logger.info(f"✓ Categoría asignada por keywords: {mejor_categoria}")
            return mejor_categoria
        else:
            logger.warning("No se encontró categoría - usando Medicina General")
            return "Medicina General"

    except Exception as e:
        logger.error(f"Error en categorización híbrida: {e}")
        return "Medicina General"
