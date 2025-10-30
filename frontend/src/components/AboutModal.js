import React from 'react';
import { useTranslation } from 'react-i18next';
import { Heart, Code, Users, Palette } from 'lucide-react';
import Modal from './ui/Modal';
import logo from '../assets/clinic-cloud-logo.png';

const AboutModal = ({ isOpen, onClose }) => {
  const { t } = useTranslation();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="md"
      showCloseButton={true}
    >
      <div className="bg-white dark:bg-gray-800">
        {/* Header con logo */}
        <div className="flex flex-col items-center mb-6">
          <img
            src={logo}
            alt="Clinic Cloud Logo"
            className="w-72 h-auto mb-2"
          />
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {t('about.version')} 1.0.0
          </p>
        </div>

        {/* Descripción */}
        <div className="mb-6">
          <p className="text-gray-700 dark:text-gray-300 text-center leading-relaxed">
            {t('about.description')}
          </p>
        </div>

        {/* Secciones */}
        <div className="space-y-4 mb-6">
          {/* Desarrollado con */}
          <div className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <Code className="w-5 h-5 text-primary-600 dark:text-primary-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                {t('about.builtWith')}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {t('about.builtWithDescription')}
              </p>
            </div>
          </div>

          {/* Equipo */}
          <div className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <Users className="w-5 h-5 text-primary-600 dark:text-primary-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                {t('about.team')}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {t('about.teamDescription')}
              </p>
            </div>
          </div>

          {/* Créditos de iconos */}
          <div className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <Palette className="w-5 h-5 text-primary-600 dark:text-primary-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                {t('about.iconCredits')}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {t('about.iconCreditsText')}{' '}
                <a
                  href="https://www.flaticon.com/authors/flat-icons"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 dark:text-primary-400 hover:underline font-medium"
                >
                  Flat Icons
                </a>
                {' '}{t('about.from')}{' '}
                <a
                  href="https://www.flaticon.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 dark:text-primary-400 hover:underline font-medium"
                >
                  Flaticon
                </a>
              </p>
            </div>
          </div>
        </div>

        {/* Footer del modal */}
        <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <Heart className="w-4 h-4 text-red-500" />
            <span>{t('about.madeWith')}</span>
          </div>
          <p className="text-center text-xs text-gray-500 dark:text-gray-400 mt-3">
            {t('about.license')}
          </p>
        </div>
      </div>
    </Modal>
  );
};

export default AboutModal;
