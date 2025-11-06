#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Templates para Sistema Híbrido de Scraping
=================================================

Este módulo contiene templates de queries médicas organizadas por categoría,
diseñadas para maximizar la diversidad y cobertura del scraping.
"""

# =====================================================
# QUERIES POR CATEGORÍA MÉDICA
# =====================================================

MEDICAL_QUERIES = {
    "Oncology": {
        "general": ["oncology", "cancer", "neoplasm", "tumor", "carcinoma"],
        "specific": [
            "breast cancer treatment", "lung cancer immunotherapy",
            "colorectal cancer screening", "prostate cancer therapy",
            "leukemia treatment", "lymphoma diagnosis",
            "melanoma prevention", "pancreatic cancer research",
            "ovarian cancer biomarkers", "brain tumor surgery",
            "cancer stem cells", "metastasis mechanisms",
            "chemotherapy resistance", "radiation oncology",
            "targeted cancer therapy", "CAR-T cell therapy"
        ],
        "mesh_terms": [
            "Neoplasms[MeSH]", "Antineoplastic Agents[MeSH]",
            "Immunotherapy[MeSH]", "Precision Medicine[MeSH]"
        ]
    },

    "Cardiology": {
        "general": ["cardiology", "heart disease", "cardiovascular"],
        "specific": [
            "myocardial infarction", "heart failure management",
            "atrial fibrillation treatment", "coronary artery disease",
            "hypertension guidelines", "arrhythmia diagnosis",
            "cardiac arrest resuscitation", "valvular heart disease",
            "congenital heart defects", "heart transplantation",
            "cardiac imaging", "interventional cardiology",
            "anticoagulation therapy", "statins cardiovascular prevention"
        ],
        "mesh_terms": [
            "Cardiovascular Diseases[MeSH]", "Myocardial Infarction[MeSH]",
            "Heart Failure[MeSH]", "Arrhythmias, Cardiac[MeSH]"
        ]
    },

    "Neurology": {
        "general": ["neurology", "neurological disorders", "brain disease"],
        "specific": [
            "Alzheimer disease treatment", "Parkinson disease therapy",
            "multiple sclerosis management", "epilepsy treatment",
            "stroke prevention", "migraine prophylaxis",
            "amyotrophic lateral sclerosis", "traumatic brain injury",
            "neuropathic pain", "peripheral neuropathy",
            "brain imaging techniques", "neurodegenerative diseases",
            "cognitive impairment", "dementia diagnosis"
        ],
        "mesh_terms": [
            "Nervous System Diseases[MeSH]", "Neurodegenerative Diseases[MeSH]",
            "Stroke[MeSH]", "Epilepsy[MeSH]"
        ]
    },

    "Endocrinology": {
        "general": ["endocrinology", "hormones", "metabolic disorders"],
        "specific": [
            "diabetes mellitus type 2", "type 1 diabetes management",
            "thyroid disorders", "hypothyroidism treatment",
            "hyperthyroidism therapy", "obesity management",
            "metabolic syndrome", "polycystic ovary syndrome",
            "adrenal insufficiency", "pituitary disorders",
            "osteoporosis prevention", "vitamin D deficiency",
            "insulin resistance", "diabetic neuropathy"
        ],
        "mesh_terms": [
            "Endocrine System Diseases[MeSH]", "Diabetes Mellitus[MeSH]",
            "Thyroid Diseases[MeSH]", "Metabolic Syndrome[MeSH]"
        ]
    },

    "Gastroenterology": {
        "general": ["gastroenterology", "digestive system", "GI disorders"],
        "specific": [
            "inflammatory bowel disease", "Crohn disease treatment",
            "ulcerative colitis management", "irritable bowel syndrome",
            "gastroesophageal reflux disease", "peptic ulcer disease",
            "hepatitis C treatment", "cirrhosis management",
            "nonalcoholic fatty liver disease", "colorectal screening",
            "celiac disease", "pancreatitis", "Barrett esophagus",
            "hepatocellular carcinoma"
        ],
        "mesh_terms": [
            "Gastrointestinal Diseases[MeSH]", "Inflammatory Bowel Diseases[MeSH]",
            "Liver Diseases[MeSH]", "Digestive System Neoplasms[MeSH]"
        ]
    },

    "Pulmonology": {
        "general": ["pulmonology", "respiratory disease", "lung disease"],
        "specific": [
            "chronic obstructive pulmonary disease", "asthma management",
            "pulmonary fibrosis", "pneumonia treatment",
            "tuberculosis diagnosis", "sleep apnea syndrome",
            "acute respiratory distress syndrome", "pulmonary embolism",
            "bronchiectasis", "pulmonary hypertension",
            "lung transplantation", "respiratory infections",
            "cystic fibrosis", "sarcoidosis"
        ],
        "mesh_terms": [
            "Respiratory Tract Diseases[MeSH]", "Lung Diseases[MeSH]",
            "Asthma[MeSH]", "Pulmonary Disease, Chronic Obstructive[MeSH]"
        ]
    },

    "Nephrology": {
        "general": ["nephrology", "kidney disease", "renal disorders"],
        "specific": [
            "chronic kidney disease", "acute kidney injury",
            "end stage renal disease", "diabetic nephropathy",
            "glomerulonephritis", "polycystic kidney disease",
            "kidney transplantation", "hemodialysis",
            "peritoneal dialysis", "nephrotic syndrome",
            "renal replacement therapy", "urinary tract infection"
        ],
        "mesh_terms": [
            "Kidney Diseases[MeSH]", "Renal Insufficiency, Chronic[MeSH]",
            "Acute Kidney Injury[MeSH]", "Kidney Transplantation[MeSH]"
        ]
    },

    "Infectious Disease": {
        "general": ["infectious disease", "infection", "antimicrobial"],
        "specific": [
            "COVID-19 treatment", "HIV AIDS management",
            "sepsis management", "antibiotic resistance",
            "healthcare associated infections", "Clostridium difficile",
            "influenza vaccination", "viral hepatitis",
            "fungal infections", "parasitic diseases",
            "emerging infectious diseases", "antimicrobial stewardship",
            "infection prevention control"
        ],
        "mesh_terms": [
            "Communicable Diseases[MeSH]", "Bacterial Infections[MeSH]",
            "Virus Diseases[MeSH]", "Anti-Infective Agents[MeSH]"
        ]
    },

    "Immunology": {
        "general": ["immunology", "immune system", "autoimmune"],
        "specific": [
            "rheumatoid arthritis treatment", "systemic lupus erythematosus",
            "autoimmune diseases", "immunodeficiency disorders",
            "allergic diseases", "transplant immunology",
            "vaccine development", "immunotherapy",
            "primary immunodeficiency", "anaphylaxis management",
            "biological therapy", "immune checkpoint inhibitors"
        ],
        "mesh_terms": [
            "Immune System Diseases[MeSH]", "Autoimmune Diseases[MeSH]",
            "Immunotherapy[MeSH]", "Immunologic Deficiency Syndromes[MeSH]"
        ]
    },

    "Hematology": {
        "general": ["hematology", "blood disorders", "hematologic"],
        "specific": [
            "anemia treatment", "iron deficiency anemia",
            "sickle cell disease", "thalassemia",
            "hemophilia management", "thrombocytopenia",
            "venous thromboembolism", "anticoagulation",
            "bone marrow transplantation", "myelodysplastic syndromes",
            "platelet disorders", "hemostasis"
        ],
        "mesh_terms": [
            "Hematologic Diseases[MeSH]", "Anemia[MeSH]",
            "Blood Coagulation Disorders[MeSH]", "Thrombosis[MeSH]"
        ]
    },

    "Dermatology": {
        "general": ["dermatology", "skin disease", "dermatologic"],
        "specific": [
            "psoriasis treatment", "atopic dermatitis",
            "acne vulgaris management", "skin cancer screening",
            "melanoma detection", "eczema treatment",
            "vitiligo therapy", "alopecia treatment",
            "wound healing", "dermatologic surgery",
            "phototherapy", "biologic agents dermatology"
        ],
        "mesh_terms": [
            "Skin Diseases[MeSH]", "Dermatitis[MeSH]",
            "Skin Neoplasms[MeSH]", "Psoriasis[MeSH]"
        ]
    },

    "Pediatrics": {
        "general": ["pediatrics", "children", "infant"],
        "specific": [
            "childhood vaccination", "pediatric obesity",
            "neonatal care", "pediatric asthma",
            "developmental disorders", "attention deficit hyperactivity disorder",
            "autism spectrum disorder", "pediatric infectious diseases",
            "growth disorders", "pediatric nutrition",
            "congenital abnormalities", "pediatric emergency medicine"
        ],
        "mesh_terms": [
            "Child[MeSH]", "Infant[MeSH]",
            "Pediatrics[MeSH]", "Child Development Disorders[MeSH]"
        ]
    },

    "Geriatrics": {
        "general": ["geriatrics", "elderly", "aging"],
        "specific": [
            "geriatric assessment", "frailty elderly",
            "polypharmacy", "falls prevention elderly",
            "dementia elderly", "sarcopenia",
            "osteoporosis elderly", "geriatric syndromes",
            "palliative care elderly", "multimorbidity"
        ],
        "mesh_terms": [
            "Aged[MeSH]", "Geriatrics[MeSH]",
            "Frailty[MeSH]", "Aging[MeSH]"
        ]
    },

    "Obstetrics Gynecology": {
        "general": ["obstetrics", "gynecology", "women's health"],
        "specific": [
            "prenatal care", "pregnancy complications",
            "preeclampsia management", "gestational diabetes",
            "cesarean section", "postpartum care",
            "menopause management", "endometriosis treatment",
            "uterine fibroids", "cervical cancer screening",
            "contraception", "infertility treatment"
        ],
        "mesh_terms": [
            "Pregnancy[MeSH]", "Genital Diseases, Female[MeSH]",
            "Obstetrics[MeSH]", "Gynecology[MeSH]"
        ]
    },

    "Rheumatology": {
        "general": ["rheumatology", "arthritis", "musculoskeletal"],
        "specific": [
            "rheumatoid arthritis biologic therapy",
            "osteoarthritis management", "gout treatment",
            "ankylosing spondylitis", "systemic sclerosis",
            "vasculitis", "fibromyalgia", "polymyalgia rheumatica",
            "disease modifying antirheumatic drugs"
        ],
        "mesh_terms": [
            "Rheumatic Diseases[MeSH]", "Arthritis, Rheumatoid[MeSH]",
            "Spondyloarthropathies[MeSH]", "Vasculitis[MeSH]"
        ]
    },

    "Ophthalmology": {
        "general": ["ophthalmology", "eye disease", "vision"],
        "specific": [
            "cataract surgery", "glaucoma management",
            "macular degeneration treatment", "diabetic retinopathy",
            "retinal detachment", "refractive surgery",
            "uveitis treatment", "corneal transplantation",
            "dry eye syndrome", "optic neuritis"
        ],
        "mesh_terms": [
            "Eye Diseases[MeSH]", "Retinal Diseases[MeSH]",
            "Glaucoma[MeSH]", "Cataract[MeSH]"
        ]
    },

    "Otolaryngology": {
        "general": ["otolaryngology", "ENT", "ear nose throat"],
        "specific": [
            "hearing loss treatment", "tinnitus management",
            "chronic sinusitis", "obstructive sleep apnea surgery",
            "laryngeal cancer", "vestibular disorders",
            "cochlear implants", "rhinoplasty",
            "tonsillectomy", "vertigo treatment"
        ],
        "mesh_terms": [
            "Otorhinolaryngologic Diseases[MeSH]", "Hearing Loss[MeSH]",
            "Sinusitis[MeSH]", "Laryngeal Diseases[MeSH]"
        ]
    },

    "Psychiatry": {
        "general": ["psychiatry", "mental health", "psychiatric disorders"],
        "specific": [
            "major depressive disorder", "bipolar disorder treatment",
            "schizophrenia management", "anxiety disorders",
            "post traumatic stress disorder", "obsessive compulsive disorder",
            "eating disorders", "substance use disorders",
            "suicide prevention", "antidepressant therapy",
            "psychotherapy", "mood disorders"
        ],
        "mesh_terms": [
            "Mental Disorders[MeSH]", "Depressive Disorder[MeSH]",
            "Schizophrenia[MeSH]", "Anxiety Disorders[MeSH]"
        ]
    },

    "Traumatology": {
        "general": ["trauma", "injury", "emergency medicine"],
        "specific": [
            "polytrauma management", "traumatic brain injury",
            "spinal cord injury", "fracture management",
            "burn treatment", "hemorrhagic shock",
            "trauma resuscitation", "pelvic fracture",
            "thoracic trauma", "abdominal trauma"
        ],
        "mesh_terms": [
            "Wounds and Injuries[MeSH]", "Fractures, Bone[MeSH]",
            "Brain Injuries, Traumatic[MeSH]", "Emergency Medicine[MeSH]"
        ]
    },

    "Urology": {
        "general": ["urology", "urological", "genitourinary"],
        "specific": [
            "benign prostatic hyperplasia", "urinary incontinence",
            "kidney stones treatment", "bladder cancer",
            "erectile dysfunction", "urinary tract infection",
            "overactive bladder", "prostate cancer screening",
            "nephrolithiasis", "neurogenic bladder"
        ],
        "mesh_terms": [
            "Urologic Diseases[MeSH]", "Prostatic Hyperplasia[MeSH]",
            "Urinary Bladder Diseases[MeSH]", "Urolithiasis[MeSH]"
        ]
    },

    "Medical Genetics": {
        "general": ["medical genetics", "genetic disorders", "genomics"],
        "specific": [
            "genetic testing", "gene therapy",
            "hereditary cancer syndromes", "pharmacogenomics",
            "rare genetic diseases", "chromosome abnormalities",
            "genetic counseling", "precision medicine genetics",
            "CRISPR therapy", "inherited metabolic disorders"
        ],
        "mesh_terms": [
            "Genetic Diseases, Inborn[MeSH]", "Genetic Testing[MeSH]",
            "Genetic Therapy[MeSH]", "Precision Medicine[MeSH]"
        ]
    },

    "General Medicine": {
        "general": ["internal medicine", "primary care", "general practice"],
        "specific": [
            "preventive medicine", "chronic disease management",
            "health screening", "lifestyle medicine",
            "medication adherence", "patient safety",
            "quality improvement healthcare", "evidence based medicine",
            "clinical decision making", "telemedicine"
        ],
        "mesh_terms": [
            "Internal Medicine[MeSH]", "Primary Health Care[MeSH]",
            "Preventive Medicine[MeSH]", "Chronic Disease[MeSH]"
        ]
    }
}

# =====================================================
# MODIFIERS / SUFIJOS PARA AUMENTAR ESPECIFICIDAD
# =====================================================

QUERY_MODIFIERS = {
    "study_types": [
        "randomized controlled trial",
        "systematic review",
        "meta-analysis",
        "clinical trial",
        "cohort study",
        "case control study"
    ],

    "aspects": [
        "diagnosis",
        "treatment",
        "therapy",
        "management",
        "prevention",
        "prognosis",
        "etiology",
        "pathophysiology",
        "epidemiology",
        "guidelines"
    ],

    "time_filters": [
        "recent advances",
        "novel therapy",
        "emerging treatment",
        "new diagnosis",
        "latest guidelines"
    ]
}

# =====================================================
# TRENDING TOPICS (Actualizables)
# =====================================================

TRENDING_TOPICS = [
    "long COVID",
    "SARS-CoV-2 variants",
    "mRNA vaccines",
    "artificial intelligence medicine",
    "telemedicine",
    "digital health",
    "monkeypox",
    "climate change health",
    "microbiome",
    "CRISPR therapeutics",
    "CAR-T cell therapy",
    "immune checkpoint inhibitors",
    "personalized medicine",
    "pharmacogenomics",
    "health equity"
]
