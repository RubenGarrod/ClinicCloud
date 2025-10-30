import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import clsx from 'clsx';
import {
  Search,
  Bookmark,
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import logo from '../../assets/clinic-cloud-icon.png';

const Sidebar = ({ onOpenHelp, onOpenSettings, onOpenAIAssistant }) => {
  const { t } = useTranslation();
  const location = useLocation();
  const { sidebarCollapsed, toggleSidebar } = useTheme();
  const { isAuthenticated } = useAuth();

  const menuItems = [
    {
      icon: Search,
      label: t('sidebar.newSearch', 'Nueva búsqueda'),
      path: '/',
    },
    // Solo mostrar favoritos si el usuario está autenticado
    ...(isAuthenticated ? [{
      icon: Bookmark,
      label: t('sidebar.favorites', 'Favoritos'),
      path: '/favorites',
    }] : []),
    // Asistente IA (solo si está autenticado)
    ...(isAuthenticated ? [{
      icon: Sparkles,
      label: t('sidebar.aiAssistant', 'Asistente IA'),
      isModal: true,
      onClick: onOpenAIAssistant,
      badge: t('aiAssistant.comingSoon', 'Próximamente'),
    }] : []),
    {
      icon: Settings,
      label: t('sidebar.settings', 'Configuración'),
      isModal: true,
      onClick: onOpenSettings,
    },
    {
      icon: HelpCircle,
      label: t('sidebar.help', 'Ayuda'),
      isModal: true,
      onClick: onOpenHelp,
    },
  ];

  const isActiveRoute = (path) => {
    if (path === '/') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div
      className={clsx(
        'bg-transparent transition-all duration-300 flex flex-col h-screen sticky top-0',
        sidebarCollapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 h-[3.5rem]">
        {!sidebarCollapsed && (
          <h2 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            {t('sidebar.navigation', 'Navegación')}
          </h2>
        )}
        <button
          onClick={toggleSidebar}
          className="p-1.5 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-3.5 h-3.5" />
          ) : (
            <ChevronLeft className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {menuItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = item.path ? isActiveRoute(item.path) : false;

          if (item.isModal) {
            return (
              <button
                key={index}
                onClick={item.onClick}
                className={clsx(
                  'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors w-full',
                  'text-gray-700 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-800',
                  sidebarCollapsed && 'justify-center'
                )}
                title={sidebarCollapsed ? item.label : undefined}
              >
                <Icon className="w-5 h-5" />
                {!sidebarCollapsed && (
                  <div className="flex items-center justify-between flex-1 ml-3">
                    <span>{item.label}</span>
                    {item.badge && (
                      <span className="ml-2 px-2 py-0.5 text-xs bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300 rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </div>
                )}
              </button>
            );
          }

          return (
            <Link
              key={item.path}
              to={item.path}
              className={clsx(
                'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                  : 'text-gray-700 hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-gray-800',
                sidebarCollapsed && 'justify-center'
              )}
              title={sidebarCollapsed ? item.label : undefined}
            >
              <Icon className="w-5 h-5" />
              {!sidebarCollapsed && (
                <span className="ml-3">{item.label}</span>
              )}
            </Link>
          );
        })}
      </nav>

    </div>
  );
};

export default Sidebar;