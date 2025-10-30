/**
 * MODAL DEL ASISTENTE IA
 * ======================
 * Modal informativo sobre la funcionalidad futura del Asistente IA
 *
 * Copyright (C) 2025 Rubén García Rodríguez
 * Licensed under GPL-3.0
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import Modal from './ui/Modal';
import { Sparkles, MessageSquare, BookOpen, History, HelpCircle } from 'lucide-react';

const AIAssistantModal = ({ isOpen, onClose }) => {
  const { t } = useTranslation();

  const features = [
    {
      icon: BookOpen,
      text: t('aiAssistant.feature1', 'Análisis profundo de documentos médicos'),
    },
    {
      icon: MessageSquare,
      text: t('aiAssistant.feature2', 'Respuestas contextualizadas basadas en evidencia'),
    },
    {
      icon: History,
      text: t('aiAssistant.feature3', 'Historial de consultas y conversaciones'),
    },
    {
      icon: HelpCircle,
      text: t('aiAssistant.feature4', 'Explicaciones simplificadas de términos médicos'),
    },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t('aiAssistant.title', 'Asistente')}>
      <div className="space-y-6">
        {/* Coming Soon Badge */}
        <div className="flex justify-center">
          <span className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 rounded-full text-sm font-medium">
            <Sparkles className="w-4 h-4" />
            {t('aiAssistant.comingSoon', 'Próximamente')}
          </span>
        </div>

        {/* Icon */}
        <div className="flex justify-center">
          <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-700 rounded-2xl flex items-center justify-center shadow-lg">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
        </div>

        {/* Title */}
        <div className="text-center">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            {t('aiAssistant.comingSoonTitle', 'Funcionalidad en desarrollo')}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
            {t('aiAssistant.comingSoonDescription', 'El Asistente te permitirá hacer preguntas específicas sobre los documentos médicos y obtener respuestas contextualizadas basadas en su contenido.')}
          </p>
        </div>

        {/* Features List */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
            {t('aiAssistant.comingSoonFeatures', 'Características que incluirá:')}
          </h4>
          <ul className="space-y-3">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <li key={index} className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center">
                    <Icon className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                  </div>
                  <span className="text-sm text-gray-700 dark:text-gray-300 pt-1">
                    {feature.text}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400 italic">
            {t('aiAssistant.stayTuned', 'Mantente atento a futuras actualizaciones')}
          </p>
        </div>
      </div>
    </Modal>
  );
};

export default AIAssistantModal;
