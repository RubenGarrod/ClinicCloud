import React from 'react';
import { useTranslation } from 'react-i18next';
import { useToast } from '../contexts/ToastContext';
import Dropdown from './ui/Dropdown';
import { Check } from 'lucide-react';
import clsx from 'clsx';
import esFlag from '../assets/es.png';
import enFlag from '../assets/en.png';

const languages = [
  { code: 'es', name: 'Español', flag: '🇪🇸', shortName: 'ES', flagImage: esFlag },
  { code: 'en', name: 'English', flag: '🇺🇸', shortName: 'EN', flagImage: enFlag },
];

const LanguageSelector = () => {
  const { i18n, t } = useTranslation();
  const toast = useToast();

  const changeLanguage = (lng) => {
    const previousLang = i18n.language;
    i18n.changeLanguage(lng);
    localStorage.setItem('i18nextLng', lng);

    // Show toast only when switching TO Spanish (from any other language)
    if (lng === 'es' && previousLang !== 'es') {
      // Delay to ensure i18n has loaded the new language
      setTimeout(() => {
        toast.info(t('language.translationNotice'), 7000);
      }, 100);
    }
  };

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

  const trigger = (
    <div className="flex items-center justify-center px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors">
      <img
        src={currentLanguage.flagImage}
        alt={currentLanguage.name}
        className="w-7 h-5 object-cover rounded-sm"
      />
    </div>
  );

  return (
    <Dropdown trigger={trigger} placement="bottom-right">
      {languages.map((language) => (
        <Dropdown.Item
          key={language.code}
          onClick={() => changeLanguage(language.code)}
          className={clsx(
            'flex items-center justify-between px-4 py-3 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors',
            i18n.language === language.code && 'bg-primary-50 dark:bg-primary-900/20 border-l-2 border-primary-500'
          )}
        >
          <div className="flex items-center">
            <img 
              src={language.flagImage} 
              alt={language.name}
              className="w-6 h-4 object-contain rounded mr-3"
            />
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {language.name}
            </span>
          </div>
          {i18n.language === language.code && (
            <div className="flex items-center justify-center w-5 h-5 bg-primary-100 dark:bg-primary-900 rounded-full">
              <Check className="w-3 h-3 text-primary-600 dark:text-primary-400" />
            </div>
          )}
        </Dropdown.Item>
      ))}
    </Dropdown>
  );
};

export default LanguageSelector;