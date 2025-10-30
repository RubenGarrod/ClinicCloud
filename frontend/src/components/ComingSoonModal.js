import React from 'react';
import { useTranslation } from 'react-i18next';
import Modal from './ui/Modal';
import Button from './ui/Button';
import { Wrench, ArrowRight } from 'lucide-react';

const ComingSoonModal = ({ isOpen, onClose, feature }) => {
  const { t } = useTranslation();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={t('comingSoon.title', 'Próximamente')}
      maxWidth="md"
    >
      <div className="text-center py-6">
        {/* Icon */}
        <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900 dark:to-primary-800 rounded-full flex items-center justify-center mb-6">
          <Wrench className="w-8 h-8 text-primary-600 dark:text-primary-400" />
        </div>

        {/* Title */}
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
          {t('comingSoon.workInProgress', 'Estamos trabajando en ello')}
        </h3>

        {/* Description */}
        <p className="text-gray-600 dark:text-gray-400 mb-2 max-w-sm mx-auto">
          {t('comingSoon.featureDescription', {
            feature: feature || t('comingSoon.thisFeature', 'esta funcionalidad'),
            defaultValue: `La funcionalidad de ${feature || 'esta característica'} está actualmente en desarrollo.`
          })}
        </p>

        <p className="text-gray-500 dark:text-gray-500 text-sm mb-6">
          {t('comingSoon.stayTuned', 'Estará disponible próximamente. ¡Gracias por tu paciencia!')}
        </p>

        {/* Features list */}
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6 text-left max-w-sm mx-auto">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            {t('comingSoon.meanwhile', 'Mientras tanto, puedes:')}
          </p>
          <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <li className="flex items-center">
              <ArrowRight className="w-4 h-4 mr-2 text-primary-500 flex-shrink-0" />
              {t('comingSoon.option1', 'Crear una cuenta con tu email')}
            </li>
            <li className="flex items-center">
              <ArrowRight className="w-4 h-4 mr-2 text-primary-500 flex-shrink-0" />
              {t('comingSoon.option2', 'Explorar la plataforma sin cuenta')}
            </li>
            <li className="flex items-center">
              <ArrowRight className="w-4 h-4 mr-2 text-primary-500 flex-shrink-0" />
              {t('comingSoon.option3', 'Guardar tus búsquedas favoritas')}
            </li>
          </ul>
        </div>

        {/* Close button */}
        <Button onClick={onClose} variant="primary" className="w-full max-w-xs mx-auto">
          {t('comingSoon.understood', 'Entendido')}
        </Button>
      </div>
    </Modal>
  );
};

export default ComingSoonModal;
