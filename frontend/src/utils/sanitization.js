/**
 * Input Sanitization Utilities
 * =============================
 *
 * Utilidades para prevenir ataques XSS y validar inputs del usuario.
 *
 * Protección contra:
 * - XSS (Cross-Site Scripting)
 * - Script injection
 * - HTML injection
 * - SQL injection (capa adicional)
 *
 * Uso:
 *   import { sanitizeInput, sanitizeHTML, validateEmail } from './utils/sanitization';
 *
 *   const cleanText = sanitizeInput(userInput);
 *   const cleanHTML = sanitizeHTML(htmlContent);
 */

import React from 'react';
import DOMPurify from 'dompurify';

/**
 * Sanitiza texto plano removiendo caracteres peligrosos.
 *
 * Usa esto para:
 * - Nombres de usuario
 * - Títulos
 * - Texto general
 *
 * @param {string} input - Texto a sanitizar
 * @returns {string} Texto sanitizado
 */
export const sanitizeInput = (input) => {
  if (!input || typeof input !== 'string') {
    return '';
  }

  return input
    .trim()
    // Remover caracteres de control
    .replace(/[\x00-\x1F\x7F]/g, '')
    // Limitar longitud (prevenir DoS)
    .slice(0, 10000);
};

/**
 * Sanitiza HTML permitiendo solo tags seguros.
 *
 * Usa esto para:
 * - Contenido rico (rich text)
 * - Descripciones con formato
 * - Comentarios con HTML limitado
 *
 * @param {string} html - HTML a sanitizar
 * @param {object} options - Opciones de DOMPurify
 * @returns {string} HTML sanitizado
 */
export const sanitizeHTML = (html, options = {}) => {
  if (!html || typeof html !== 'string') {
    return '';
  }

  const defaultOptions = {
    // Tags permitidos (whitelist)
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'code', 'pre'],
    // Atributos permitidos
    ALLOWED_ATTR: ['href', 'title', 'target'],
    // Prevenir DOM clobbering
    SANITIZE_DOM: true,
    // Mantener espacios
    KEEP_CONTENT: true,
    ...options
  };

  return DOMPurify.sanitize(html, defaultOptions);
};

/**
 * Sanitiza HTML estrictamente (solo texto, sin tags).
 *
 * Usa esto para:
 * - Búsquedas
 * - Campos de formulario sensibles
 * - Cualquier lugar donde NO se permita HTML
 *
 * @param {string} html - HTML a sanitizar
 * @returns {string} Texto plano sin HTML
 */
export const sanitizeToText = (html) => {
  if (!html || typeof html !== 'string') {
    return '';
  }

  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [], // Sin tags
    ALLOWED_ATTR: [], // Sin atributos
    KEEP_CONTENT: true // Mantener contenido de texto
  });
};

/**
 * Valida email con regex seguro.
 *
 * @param {string} email - Email a validar
 * @returns {object} { valid: boolean, error: string|null }
 */
export const validateEmail = (email) => {
  if (!email || typeof email !== 'string') {
    return { valid: false, error: 'Email is required' };
  }

  // Regex RFC 5322 simplificado
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

  if (!emailRegex.test(email)) {
    return { valid: false, error: 'Invalid email format' };
  }

  if (email.length > 254) {
    return { valid: false, error: 'Email must not exceed 254 characters' };
  }

  return { valid: true, error: null };
};

/**
 * Valida contraseña según requisitos de seguridad.
 *
 * Requisitos:
 * - Mínimo 8 caracteres
 * - Al menos una mayúscula
 * - Al menos una minúscula
 * - Al menos un número
 * - Al menos un carácter especial
 *
 * @param {string} password - Contraseña a validar
 * @returns {object} { valid: boolean, errors: string[] }
 */
export const validatePassword = (password) => {
  const errors = [];

  if (!password || typeof password !== 'string') {
    return { valid: false, errors: ['Password is required'] };
  }

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }

  if (password.length > 128) {
    errors.push('Password must not exceed 128 characters');
  }

  return {
    valid: errors.length === 0,
    errors
  };
};

/**
 * Valida nombre de usuario.
 *
 * Requisitos:
 * - 3-50 caracteres
 * - Solo letras, números, guiones y guiones bajos
 * - No puede empezar/terminar con guión
 *
 * @param {string} username - Nombre de usuario a validar
 * @returns {boolean} true si es válido
 */
export const validateUsername = (username) => {
  if (!username || typeof username !== 'string') {
    return false;
  }

  const usernameRegex = /^[a-zA-Z0-9]([a-zA-Z0-9_-]{1,48}[a-zA-Z0-9])?$/;
  return usernameRegex.test(username);
};

/**
 * Escapa caracteres especiales para prevenir injection.
 *
 * Usa esto como capa adicional de seguridad.
 *
 * @param {string} input - Texto a escapar
 * @returns {string} Texto escapado
 */
export const escapeSpecialChars = (input) => {
  if (!input || typeof input !== 'string') {
    return '';
  }

  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
  };

  return input.replace(/[&<>"'/]/g, (char) => map[char]);
};

/**
 * Valida URL para prevenir javascript: y data: schemes.
 *
 * @param {string} url - URL a validar
 * @returns {boolean} true si es válida y segura
 */
export const validateURL = (url) => {
  if (!url || typeof url !== 'string') {
    return false;
  }

  // Prevenir javascript:, data:, vbscript:, etc.
  const dangerousSchemes = /^(javascript|data|vbscript|file|about):/i;
  if (dangerousSchemes.test(url)) {
    return false;
  }

  try {
    const parsed = new URL(url);
    // Solo permitir http y https
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
};

/**
 * Limita longitud de texto para prevenir DoS.
 *
 * @param {string} text - Texto a limitar
 * @param {number} maxLength - Longitud máxima
 * @returns {string} Texto limitado
 */
export const limitLength = (text, maxLength = 10000) => {
  if (!text || typeof text !== 'string') {
    return '';
  }

  return text.slice(0, maxLength);
};

/**
 * Hook de React para sanitizar inputs automáticamente.
 *
 * Uso:
 *   const [value, setValue] = useSanitizedInput('');
 *   <input value={value} onChange={(e) => setValue(e.target.value)} />
 *
 * @param {string} initialValue - Valor inicial
 * @returns {[string, function]} [value, setValue]
 */
export const useSanitizedInput = (initialValue = '') => {
  const [value, setValueInternal] = React.useState(sanitizeInput(initialValue));

  const setValue = (newValue) => {
    setValueInternal(sanitizeInput(newValue));
  };

  return [value, setValue];
};

// Exportar configuración default de DOMPurify para casos custom
export const getDOMPurifyConfig = (mode = 'default') => {
  const configs = {
    default: {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'code', 'pre'],
      ALLOWED_ATTR: ['href', 'title', 'target'],
      SANITIZE_DOM: true,
      KEEP_CONTENT: true
    },
    strict: {
      ALLOWED_TAGS: [],
      ALLOWED_ATTR: [],
      KEEP_CONTENT: true
    },
    markdown: {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'],
      ALLOWED_ATTR: ['href', 'title', 'target'],
      SANITIZE_DOM: true,
      KEEP_CONTENT: true
    }
  };

  return configs[mode] || configs.default;
};
