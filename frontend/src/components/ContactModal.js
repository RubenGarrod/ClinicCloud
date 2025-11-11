/**
 * MODAL DE CONTACTO
 * =================
 * Formulario para enviar mensajes de contacto
 * Envía un email a cliniccloud.contact@gmail.com
 *
 * Copyright (C) 2025 Rubén García Rodríguez
 * Licensed under GPL-3.0
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import authService from '../services/authService';
import Modal from './ui/Modal';
import Button from './ui/Button';
import { Mail, Send, User } from 'lucide-react';

const ContactModal = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const { user, isAuthenticated } = useAuth();
  const toast = useToast();

  const [formData, setFormData] = useState({
    subject: '',
    message: '',
    email: isAuthenticated && user?.email ? user.email : '',
    name: isAuthenticated && user?.name ? user.name : ''
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.subject.trim()) {
      newErrors.subject = t('contact.subjectRequired', 'El asunto es obligatorio');
    }

    if (!formData.message.trim()) {
      newErrors.message = t('contact.messageRequired', 'El mensaje es obligatorio');
    } else if (formData.message.trim().length < 10) {
      newErrors.message = t('contact.messageTooShort', 'El mensaje debe tener al menos 10 caracteres');
    }

    if (!formData.email.trim()) {
      newErrors.email = t('contact.emailRequired', 'El email es obligatorio');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = t('contact.invalidEmail', 'Email inválido');
    }

    if (!formData.name.trim()) {
      newErrors.name = t('contact.nameRequired', 'El nombre es obligatorio');
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
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(isAuthenticated ? authService.getAuthHeaders() : {}),
        },
        body: JSON.stringify({
          subject: formData.subject,
          message: formData.message,
          email: formData.email,
          name: formData.name,
          user_id: isAuthenticated ? user?.id : null
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          console.log('Token expirado, cerrando formulario');
          onClose();
          return;
        }
        throw new Error(t('contact.sendError', 'Error al enviar el mensaje'));
      }

      toast.success(t('contact.sendSuccess', 'Mensaje enviado correctamente'));

      // Limpiar formulario
      setFormData({
        subject: '',
        message: '',
        email: isAuthenticated && user?.email ? user.email : '',
        name: isAuthenticated && user?.name ? user.name : ''
      });

      onClose();
    } catch (error) {
      console.error('Error sending contact message:', error);
      toast.error(error.message || t('contact.sendError', 'Error al enviar el mensaje'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Limpiar error del campo cuando el usuario empiece a escribir
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="md"
      showCloseButton={true}
    >
      <div className="bg-white dark:bg-gray-800">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
            <Mail className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {t('contact.title', 'Contacto')}
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('contact.subtitle', 'Envíanos un mensaje')}
            </p>
          </div>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Nombre */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('contact.name', 'Nombre')} <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder={t('contact.namePlaceholder', 'Tu nombre')}
                className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${
                  errors.name ? 'border-red-500' : 'border-gray-300'
                }`}
              />
            </div>
            {errors.name && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.name}</p>
            )}
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('contact.email', 'Email')} <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder={t('contact.emailPlaceholder', 'tu@email.com')}
                className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
              />
            </div>
            {errors.email && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.email}</p>
            )}
          </div>

          {/* Asunto */}
          <div>
            <label htmlFor="subject" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('contact.subject', 'Asunto')} <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="subject"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              placeholder={t('contact.subjectPlaceholder', 'Asunto de tu mensaje')}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${
                errors.subject ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.subject && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.subject}</p>
            )}
          </div>

          {/* Mensaje */}
          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {t('contact.message', 'Mensaje')} <span className="text-red-500">*</span>
            </label>
            <textarea
              id="message"
              name="message"
              value={formData.message}
              onChange={handleChange}
              rows={6}
              placeholder={t('contact.messagePlaceholder', 'Escribe tu mensaje aquí...')}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white resize-none ${
                errors.message ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.message && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.message}</p>
            )}
          </div>

          {/* Botones */}
          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              {t('common.cancel', 'Cancelar')}
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting}
              icon={Send}
            >
              {isSubmitting ? t('contact.sending', 'Enviando...') : t('contact.send', 'Enviar')}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default ContactModal;
