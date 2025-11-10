import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { HelpCircle, Book, MessageCircle, FileText, Mail } from 'lucide-react';
import Modal from './ui/Modal';
import ContactModal from './ContactModal';

const HelpModal = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);

  const handleSectionClick = (index) => {
    switch(index) {
      case 1: // FAQ
        // TODO: Implementar modal de FAQ
        alert(t('help.faqComingSoon', 'Las preguntas frecuentes se están recopilando de los mensajes de contacto. ¡Pronto disponible!'));
        break;
      case 3: // Contact
        setIsContactModalOpen(true);
        break;
      default:
        // Por ahora, las otras secciones no hacen nada
        break;
    }
  };

  // Definir las secciones directamente en el render para que se actualicen con el idioma
  const helpSections = React.useMemo(() => [
    {
      icon: Book,
      title: t('help.gettingStarted'),
      description: t('help.gettingStartedDesc')
    },
    {
      icon: MessageCircle,
      title: t('help.faq'),
      description: t('help.faqDesc')
    },
    {
      icon: FileText,
      title: t('help.documentation'),
      description: t('help.documentationDesc')
    },
    {
      icon: Mail,
      title: t('help.contact'),
      description: t('help.contactDesc')
    }
  ], [t]);

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
            <HelpCircle className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {t('help.title')}
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('help.subtitle')}
            </p>
          </div>
        </div>

        {/* Help Sections */}
        <div className="space-y-4 max-h-[60vh] overflow-y-auto">
          {helpSections.map((section, index) => {
            const Icon = section.icon;
            return (
              <button
                key={index}
                onClick={() => handleSectionClick(index)}
                className="w-full text-left p-4 bg-gray-50 dark:bg-gray-900 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">
                      {section.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {section.description}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Contact Modal */}
        <ContactModal
          isOpen={isContactModalOpen}
          onClose={() => setIsContactModalOpen(false)}
        />

        {/* Footer */}
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
            {t('help.footer')}{' '}
            <button
              onClick={() => setIsContactModalOpen(true)}
              className="text-primary-600 dark:text-primary-400 hover:underline font-medium cursor-pointer bg-transparent border-none p-0"
            >
              {t('help.contactUs')}
            </button>
          </p>
        </div>
      </div>
    </Modal>
  );
};

export default HelpModal;
