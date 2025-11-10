import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { HelpCircle, Book, MessageCircle, FileText, Mail, ExternalLink } from 'lucide-react';
import Modal from './ui/Modal';
import ContactModal from './ContactModal';

const HelpModal = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [isDocumentationModalOpen, setIsDocumentationModalOpen] = useState(false);
  const [isGettingStartedModalOpen, setIsGettingStartedModalOpen] = useState(false);

  const handleSectionClick = (index) => {
    switch(index) {
      case 0: // Getting Started
        setIsGettingStartedModalOpen(true);
        break;
      case 1: // FAQ
        // TODO: Implementar modal de FAQ
        alert(t('help.faqComingSoon', 'Las preguntas frecuentes se están recopilando de los mensajes de contacto. ¡Pronto disponible!'));
        break;
      case 2: // Documentation
        setIsDocumentationModalOpen(true);
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

        {/* Getting Started Modal */}
        <Modal
          isOpen={isGettingStartedModalOpen}
          onClose={() => setIsGettingStartedModalOpen(false)}
          size="lg"
          showCloseButton={true}
        >
          <div className="bg-white dark:bg-gray-800">
            {/* Header */}
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                <Book className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {t('help.gettingStarted')}
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {t('help.gettingStartedSubtitle', 'Guía rápida para usar ClinicCloud')}
                </p>
              </div>
            </div>

            {/* Content */}
            <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-2">
              {/* Sección 1: Búsqueda */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm mr-3">1</span>
                  {t('guide.searchTitle', 'Realizar una búsqueda')}
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {t('guide.searchDesc', 'Ingresa términos médicos en español o inglés en la barra de búsqueda. El sistema utiliza búsqueda semántica para encontrar los documentos más relevantes.')}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                  <li>{t('guide.searchTip1', 'Puedes buscar síntomas, enfermedades, tratamientos, etc.')}</li>
                  <li>{t('guide.searchTip2', 'No necesitas usar términos exactos, la búsqueda es inteligente')}</li>
                  <li>{t('guide.searchTip3', 'Los resultados se ordenan por relevancia automáticamente')}</li>
                </ul>
              </div>

              {/* Sección 2: Filtros */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm mr-3">2</span>
                  {t('guide.filtersTitle', 'Filtrar y ordenar resultados')}
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {t('guide.filtersDesc', 'Refina tus resultados usando los filtros disponibles en la página de resultados:')}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                  <li>{t('guide.filtersTip1', 'Filtra por categoría médica (cardiología, neurología, etc.)')}</li>
                  <li>{t('guide.filtersTip2', 'Ordena por relevancia, fecha o autor')}</li>
                  <li>{t('guide.filtersTip3', 'Ajusta el número de resultados por página')}</li>
                </ul>
              </div>

              {/* Sección 3: Favoritos */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm mr-3">3</span>
                  {t('guide.favoritesTitle', 'Guardar documentos favoritos')}
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {t('guide.favoritesDesc', 'Guarda los documentos más importantes para acceder a ellos rápidamente:')}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                  <li>{t('guide.favoritesTip1', 'Haz clic en el icono de estrella para agregar a favoritos')}</li>
                  <li>{t('guide.favoritesTip2', 'Accede a tus favoritos desde el menú lateral')}</li>
                  <li>{t('guide.favoritesTip3', 'Requiere iniciar sesión para usar esta función')}</li>
                </ul>
              </div>

              {/* Sección 4: Historial */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm mr-3">4</span>
                  {t('guide.historyTitle', 'Consultar historial de búsquedas')}
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {t('guide.historyDesc', 'Revisa tus búsquedas anteriores y vuelve a ejecutarlas fácilmente:')}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                  <li>{t('guide.historyTip1', 'El historial guarda automáticamente tus búsquedas')}</li>
                  <li>{t('guide.historyTip2', 'Haz clic en cualquier búsqueda para repetirla')}</li>
                  <li>{t('guide.historyTip3', 'Configura el tiempo de retención en ajustes')}</li>
                </ul>
              </div>

              {/* Sección 5: Preferencias */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                  <span className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm mr-3">5</span>
                  {t('guide.settingsTitle', 'Personalizar preferencias')}
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {t('guide.settingsDesc', 'Ajusta la aplicación a tus necesidades desde el panel de configuración:')}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                  <li>{t('guide.settingsTip1', 'Cambia el idioma de la interfaz (español/inglés)')}</li>
                  <li>{t('guide.settingsTip2', 'Selecciona tema claro, oscuro o automático')}</li>
                  <li>{t('guide.settingsTip3', 'Ajusta el tamaño de fuente para mejor legibilidad')}</li>
                </ul>
              </div>
            </div>
          </div>
        </Modal>

        {/* Contact Modal */}
        <ContactModal
          isOpen={isContactModalOpen}
          onClose={() => setIsContactModalOpen(false)}
        />

        {/* Documentation Modal */}
        <Modal
          isOpen={isDocumentationModalOpen}
          onClose={() => setIsDocumentationModalOpen(false)}
          size="lg"
          showCloseButton={true}
        >
          <div className="bg-white dark:bg-gray-800">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                  <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {t('help.documentation')}
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {t('help.documentationSubtitle', 'Documentación completa del proyecto')}
                  </p>
                </div>
              </div>
              <a
                href="https://github.com/Reub26/ClinicCloud#readme"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 text-primary-600 dark:text-primary-400 hover:underline"
              >
                <span className="text-sm font-medium">{t('help.openInGitHub', 'Abrir en GitHub')}</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            {/* Iframe con README */}
            <div className="w-full h-[70vh] border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <iframe
                src="https://github.com/Reub26/ClinicCloud/blob/main/README.md"
                className="w-full h-full"
                title="Documentation"
                sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
              />
            </div>

            {/* Info note */}
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-300">
                {t('help.documentationNote', 'Si tienes problemas visualizando la documentación aquí, puedes abrirla directamente en GitHub usando el enlace de arriba.')}
              </p>
            </div>
          </div>
        </Modal>

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
