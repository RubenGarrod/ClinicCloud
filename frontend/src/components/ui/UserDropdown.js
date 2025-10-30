import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  User,
  Settings,
  History,
  HelpCircle,
  LogOut,
  ChevronDown
} from 'lucide-react';
import { getAvatarIcon, getAvatarColorClass, getDefaultAvatar } from '../../utils/avatarUtils';

const UserDropdown = ({ user, onLogout, onOpenProfile, onOpenHelp, className = '' }) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const dropdownRef = useRef(null);
  const currentAvatar = user?.avatar || getDefaultAvatar();

  // Cerrar dropdown al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleProfileClick = () => {
    setIsOpen(false);
    if (onOpenProfile) {
      onOpenProfile();
    }
  };

  const handleHelpClick = () => {
    setIsOpen(false);
    if (onOpenHelp) {
      onOpenHelp();
    }
  };

  const menuItems = [
    {
      icon: User,
      label: t('userMenu.profile', 'Perfil'),
      isModal: true,
      onClick: handleProfileClick
    },
    {
      icon: History,
      label: t('userMenu.searchHistory', 'Historial de búsquedas'),
      path: '/history',
      onClick: () => setIsOpen(false)
    },
    {
      icon: Settings,
      label: t('userMenu.settings', 'Configuración'),
      path: '/settings',
      onClick: () => setIsOpen(false)
    },
    {
      icon: HelpCircle,
      label: t('userMenu.help', 'Ayuda'),
      isModal: true,
      onClick: handleHelpClick
    }
  ];

  const handleLogoutClick = () => {
    setIsOpen(false);
    setShowLogoutConfirm(true);
  };

  const handleConfirmLogout = () => {
    setShowLogoutConfirm(false);
    onLogout();
  };

  const handleCancelLogout = () => {
    setShowLogoutConfirm(false);
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-center px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
      >
        {/* Avatar */}
        <div className={`w-6 h-6 rounded-md flex items-center justify-center p-1 ${getAvatarColorClass(currentAvatar.color)}`}>
          <img
            src={getAvatarIcon(currentAvatar.icon)}
            alt={user?.name}
            className="w-full h-full object-contain"
          />
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-[9999]">
          <div className="py-1">
            {/* User Info Header */}
            <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {user?.name || t('userMenu.user', 'Usuario')}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {user?.email}
              </p>
            </div>

            {/* Menu Items */}
            <div className="py-1">
              {menuItems.map((item, index) => {
                const Icon = item.icon;

                if (item.isModal) {
                  return (
                    <button
                      key={index}
                      onClick={item.onClick}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-left"
                    >
                      <Icon className="w-4 h-4 mr-3 text-gray-500 dark:text-gray-400" />
                      {item.label}
                    </button>
                  );
                }

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={item.onClick}
                    className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <Icon className="w-4 h-4 mr-3 text-gray-500 dark:text-gray-400" />
                    {item.label}
                  </Link>
                );
              })}
            </div>

            {/* Logout */}
            <div className="border-t border-gray-200 dark:border-gray-700 py-1">
              <button
                onClick={handleLogoutClick}
                className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <LogOut className="w-4 h-4 mr-3" />
                {t('userMenu.logout', 'Cerrar sesión')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Logout Confirmation Dialog */}
      {showLogoutConfirm && (
        <div className="fixed inset-0 z-[9999] overflow-y-auto">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
            onClick={handleCancelLogout}
          />

          {/* Dialog */}
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                {t('userMenu.logoutConfirm', '¿Estás seguro de que quieres cerrar sesión?')}
              </h3>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={handleCancelLogout}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                >
                  {t('userMenu.logoutCancel', 'Cancelar')}
                </button>
                <button
                  onClick={handleConfirmLogout}
                  className="px-4 py-2 text-sm font-medium text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg transition-colors"
                >
                  {t('userMenu.logoutConfirmButton', 'Cerrar sesión')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserDropdown;