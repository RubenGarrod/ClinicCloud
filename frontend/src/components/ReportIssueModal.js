/**
 * MODAL PARA REPORTAR PROBLEMAS
 * ==============================
 * Formulario para reportar problemas o sugerir mejoras
 * Envía un email a cliniccloud.contact@gmail.com
 *
 * Copyright (C) 2025 Rubén García Rodríguez
 * Licensed under GPL-3.0
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import Modal from './ui/Modal';
import Button from './ui/Button';
import { AlertCircle, Send, Mail, User } from 'lucide-react';

const ReportIssueModal = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const { user, isAuthenticated } = useAuth();
  const toast = useToast();

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    email: '',
    includeUserInfo: isAuthenticated
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = t('reportIssue.titleRequired', 'El título es obligatorio');
    }

    if (!formData.description.trim()) {
      newErrors.description = t('reportIssue.descriptionRequired', 'La descripción es obligatoria');
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = t('reportIssue.invalidEmail', 'Email inválido');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Preparar datos para enviar
      const requestData = {
        title: formData.title,
        description: formData.description,
        include_user_info: formData.includeUserInfo,
        contact_email: !isAuthenticated ? formData.email || null : null
      };

      // Enviar a la API
      const apiUrl = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/report-issue`;
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(isAuthenticated ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {})
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al enviar el reporte');
      }

      // Mostrar mensaje de éxito
      toast.success(t('reportIssue.success', 'Reporte enviado correctamente'));

      // Resetear formulario
      setFormData({
        title: '',
        description: '',
        email: '',
        includeUserInfo: isAuthenticated
      });

      // Cerrar modal
      setTimeout(() => {
        onClose();
      }, 500);

    } catch (error) {
      console.error('Error al enviar reporte:', error);
      toast.error(t('reportIssue.error', 'Error al enviar el reporte'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    // Limpiar error del campo al escribir
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t('reportIssue.title', 'Reportar un problema')}>
      <div className="space-y-6">
        {/* Description */}
        <div className="flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-blue-800 dark:text-blue-200">
            {t('reportIssue.description', 'Ayúdanos a mejorar ClinicCloud reportando problemas o sugiriendo mejoras')}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('reportIssue.titleLabel', 'Título')}
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder={t('reportIssue.titlePlaceholder', 'Breve descripción del problema')}
              className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
                errors.title ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.title}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('reportIssue.descriptionLabel', 'Descripción detallada')}
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder={t('reportIssue.descriptionPlaceholder', 'Describe el problema que encontraste o la mejora que sugieres...')}
              rows={6}
              className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors resize-y ${
                errors.description ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.description}</p>
            )}
          </div>

          {/* Email - Solo si no está autenticado */}
          {!isAuthenticated && (
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('reportIssue.emailLabel', 'Email (opcional)')}
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder={t('reportIssue.emailPlaceholder', 'tu@email.com')}
                  className={`w-full pl-10 pr-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors ${
                    errors.email ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                  }`}
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.email}</p>
              )}
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {t('reportIssue.emailHelp', 'Déjanos tu email si quieres que te respondamos')}
              </p>
            </div>
          )}

          {/* Include User Info - Solo si está autenticado */}
          {isAuthenticated && (
            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <input
                type="checkbox"
                id="includeUserInfo"
                name="includeUserInfo"
                checked={formData.includeUserInfo}
                onChange={handleChange}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="includeUserInfo" className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
                <User className="w-4 h-4" />
                {t('reportIssue.includeUserInfo', 'Incluir mi información de usuario')}
              </label>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              className="flex-1"
              disabled={isSubmitting}
            >
              {t('reportIssue.cancel', 'Cancelar')}
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1 flex items-center justify-center gap-2"
              disabled={isSubmitting}
            >
              <Send className="w-4 h-4" />
              {isSubmitting
                ? t('reportIssue.submitting', 'Enviando...')
                : t('reportIssue.submit', 'Enviar reporte')
              }
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default ReportIssueModal;
