import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

// Cache de traducciones para evitar llamadas repetidas a la API
const translationCache = new Map();

// Control de rate limiting para MyMemory API
let requestQueue = [];
let isProcessingQueue = false;
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 500; // Mínimo 500ms entre peticiones (máx 2 peticiones/segundo)
let apiErrorCount = 0;
let apiDisabledUntil = 0; // Timestamp cuando se puede volver a usar la API

// APIs de traducción gratuitas (ordenadas por preferencia)
// 1. MyMemory API - Gratis, sin registro, buena calidad
// 2. LibreTranslate - Open source (requiere instancia propia o usar público)
// FUTURO: Google Translate API (de pago, mejor calidad para textos médicos)

// Diccionarios de traducción básicos (fallback rápido)
const esEnDict = {
  // Categorías médicas
  "Oncología": "Oncology",
  "Cardiología": "Cardiology",
  "Neurología": "Neurology",
  "Endocrinología": "Endocrinology",
  "Gastroenterología": "Gastroenterology",
  "Neumología": "Pulmonology",
  "Nefrología": "Nephrology",
  "Infectología": "Infectious Disease",
  "Inmunología": "Immunology",
  "Hematología": "Hematology",
  "Dermatología": "Dermatology",
  "Pediatría": "Pediatrics",
  "Geriatría": "Geriatrics",
  "Obstetricia y Ginecología": "Obstetrics and Gynecology",
  "Reumatología": "Rheumatology",
  "Oftalmología": "Ophthalmology",
  "Otorrinolaringología": "Otolaryngology",
  "Psiquiatría": "Psychiatry",
  "Traumatología": "Traumatology",
  "Urología": "Urology",
  "Genética Médica": "Medical Genetics",
  "Medicina General": "General Medicine",
  
  // Términos médicos comunes
  "tratamiento": "treatment",
  "enfermedad": "disease",
  "paciente": "patient",
  "pacientes": "patients",
  "estudio": "study",
  "estudios": "studies",
  "investigación": "research",
  "médico": "medical",
  "clínico": "clinical",
  "análisis": "analysis",
  "resultados": "results",
  "síntomas": "symptoms",
  "diagnóstico": "diagnosis",
  "terapia": "therapy",
  "hospital": "hospital"
};

const enEsDict = {
  // Categorías médicas inversas
  "Oncology": "Oncología",
  "Cardiology": "Cardiología",
  "Neurology": "Neurología",
  "Endocrinology": "Endocrinología",
  "Gastroenterology": "Gastroenterología",
  "Pulmonology": "Neumología",
  "Nephrology": "Nefrología",
  "Infectious Disease": "Infectología",
  "Immunology": "Inmunología",
  "Hematology": "Hematología",
  "Dermatology": "Dermatología",
  "Pediatrics": "Pediatría",
  "Geriatrics": "Geriatría",
  "Obstetrics and Gynecology": "Obstetricia y Ginecología",
  "Rheumatology": "Reumatología",
  "Ophthalmology": "Oftalmología",
  "Otolaryngology": "Otorrinolaringología",
  "Psychiatry": "Psiquiatría",
  "Traumatology": "Traumatología",
  "Urology": "Urología",
  "Medical Genetics": "Genética Médica",
  "General Medicine": "Medicina General",
  
  // Términos médicos comunes
  "treatment": "tratamiento",
  "disease": "enfermedad",
  "patient": "paciente",
  "patients": "pacientes",
  "study": "estudio",
  "studies": "estudios",
  "research": "investigación",
  "medical": "médico",
  "clinical": "clínico",
  "analysis": "análisis",
  "results": "resultados",
  "symptoms": "síntomas",
  "diagnosis": "diagnóstico",
  "therapy": "terapia",
  "hospital": "hospital"
};

// Función para traducir texto usando diccionarios (fallback rápido)
const translateWithDict = (text, fromLang, toLang) => {
  if (!text) return text;

  // Elegir el diccionario adecuado
  const dict = (fromLang === 'es' && toLang === 'en') ? esEnDict :
               (fromLang === 'en' && toLang === 'es') ? enEsDict : null;

  if (!dict) return text; // No hay diccionario para esta combinación

  // Para categorías y términos exactos
  if (dict[text]) return dict[text];

  // Para textos más largos, reemplazar palabras
  let translatedText = text;

  // Ordenar las claves por longitud (descendente) para evitar reemplazos parciales
  const sortedKeys = Object.keys(dict).sort((a, b) => b.length - a.length);

  for (const key of sortedKeys) {
    // Usar expresión regular para reemplazar palabras completas (con límites de palabra)
    const regex = new RegExp(`\\b${key}\\b`, 'gi');
    translatedText = translatedText.replace(regex, dict[key]);
  }

  return translatedText;
};

// Función para traducir usando MyMemory API (gratis) con rate limiting
const translateWithMyMemory = async (text, fromLang, toLang) => {
  try {
    // Si la API está temporalmente deshabilitada por demasiados errores
    if (Date.now() < apiDisabledUntil) {
      console.log('MyMemory API temporalmente deshabilitada, usando fallback');
      return null;
    }

    // Respetar el rate limit
    const now = Date.now();
    const timeSinceLastRequest = now - lastRequestTime;
    if (timeSinceLastRequest < MIN_REQUEST_INTERVAL) {
      // Esperar el tiempo necesario
      await new Promise(resolve => setTimeout(resolve, MIN_REQUEST_INTERVAL - timeSinceLastRequest));
    }

    lastRequestTime = Date.now();

    const langPair = `${fromLang}|${toLang}`;
    const encodedText = encodeURIComponent(text);

    const response = await fetch(
      `https://api.mymemory.translated.net/get?q=${encodedText}&langpair=${langPair}`
    );

    // Manejar error 429 (Too Many Requests)
    if (response.status === 429) {
      apiErrorCount++;
      console.warn(`MyMemory API rate limit alcanzado (error ${apiErrorCount})`);

      // Si hay muchos errores 429, deshabilitar la API por 1 minuto
      if (apiErrorCount >= 3) {
        apiDisabledUntil = Date.now() + 60000; // 1 minuto
        console.warn('MyMemory API deshabilitada por 1 minuto debido a rate limiting');
      }

      return null;
    }

    if (!response.ok) {
      throw new Error(`MyMemory API error: ${response.status}`);
    }

    const data = await response.json();

    if (data.responseStatus === 200 && data.responseData?.translatedText) {
      // Resetear contador de errores si la petición fue exitosa
      apiErrorCount = 0;
      return data.responseData.translatedText;
    }

    throw new Error('Translation failed');
  } catch (error) {
    console.error('MyMemory translation error:', error);
    return null;
  }
};

// Función principal de traducción con múltiples estrategias
const translateText = async (text, fromLang, toLang) => {
  if (!text || text.length === 0) return text;

  // Crear clave de caché
  const cacheKey = `${fromLang}-${toLang}-${text}`;

  // Verificar caché primero (esto evita llamadas duplicadas a la API)
  if (translationCache.has(cacheKey)) {
    return translationCache.get(cacheKey);
  }

  // SIEMPRE intentar diccionario primero (es instantáneo y no consume rate limit)
  const dictTranslation = translateWithDict(text, fromLang, toLang);
  if (dictTranslation !== text) {
    translationCache.set(cacheKey, dictTranslation);
    return dictTranslation;
  }

  // Solo usar API si:
  // 1. El texto no está en el diccionario
  // 2. El texto es suficientemente largo para justificar el uso de API
  // 3. La API no está deshabilitada temporalmente
  if (text.length > 20 && Date.now() >= apiDisabledUntil) {
    try {
      const apiTranslation = await translateWithMyMemory(text, fromLang, toLang);

      if (apiTranslation) {
        translationCache.set(cacheKey, apiTranslation);
        return apiTranslation;
      }
    } catch (error) {
      console.error('API translation failed, using original text', error);
    }
  }

  // Si la API falló o está deshabilitada, devolver texto original
  // (ya que el diccionario no encontró una traducción)
  translationCache.set(cacheKey, text);
  return text;
};

const DynamicTranslation = ({ children, contentLanguage }) => {
  const { i18n } = useTranslation();
  const [translatedContent, setTranslatedContent] = useState(children);
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    // Si no hay contenido o no es string, no traducir
    if (!children || typeof children !== 'string') {
      setTranslatedContent(children);
      return;
    }

    // Si el idioma actual es el mismo que el del contenido, no traducir
    if (i18n.language === contentLanguage) {
      setTranslatedContent(children);
      return;
    }

    // Función asíncrona para traducir
    const performTranslation = async () => {
      setIsTranslating(true);

      try {
        const translated = await translateText(children, contentLanguage, i18n.language);
        setTranslatedContent(translated);
      } catch (error) {
        console.error('Translation error:', error);
        // En caso de error, mostrar el texto original
        setTranslatedContent(children);
      } finally {
        setIsTranslating(false);
      }
    };

    performTranslation();

  }, [children, i18n.language, contentLanguage]);

  if (isTranslating) {
    return <span className="opacity-70">{children}</span>;
  }

  return <>{translatedContent}</>;
};

export default DynamicTranslation;