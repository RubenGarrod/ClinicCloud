import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import LanguageSelector from '../LanguageSelector';
import LoginModal from '../LoginModal';
import ProfileModal from '../ProfileModal';
import HelpModal from '../HelpModal';
import { Moon, Sun, Menu, LogIn } from 'lucide-react';
import Button from '../ui/Button';
import UserDropdown from '../ui/UserDropdown';
import logo from '../../assets/clinic-cloud-icon.png';

const TopBar = ({ onOpenHelpModal }) => {
  const { isDark, toggleTheme, toggleSidebar } = useTheme();
  const { user, isAuthenticated, logout } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    }
  };

  return (
    <header className="bg-transparent px-4 h-[3.5rem] flex items-center sticky top-0 z-50">
      <div className="flex items-center justify-between w-full">
        {/* Left side - Mobile menu button and Logo */}
        <div className="flex items-center">
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 mr-3"
          >
            <Menu className="w-5 h-5" />
          </button>
          
          {/* App Logo and Name */}
          <Link to="/" className="flex items-center">
            <img src={logo} alt="Clinic Cloud" className="w-8 h-8" />
            <span className="ml-3 text-xl font-bold text-primary-600 dark:text-primary-400 hidden sm:block">
              Clinic Cloud
            </span>
          </Link>
        </div>

        {/* Right side - Theme toggle, Language selector and Auth */}
        <div className="flex items-center space-x-2">
          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            className="px-3 py-2"
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? (
              <Sun className="w-5 h-5" />
            ) : (
              <Moon className="w-5 h-5" />
            )}
          </Button>

          {/* Language Selector */}
          <LanguageSelector />

          {/* Divider */}
          <div className="h-6 w-px bg-gray-300 dark:bg-gray-600 mx-1"></div>

          {/* Auth Section */}
          {isAuthenticated ? (
            <UserDropdown
              user={user}
              onLogout={handleLogout}
              onOpenProfile={() => setIsProfileModalOpen(true)}
              onOpenHelp={onOpenHelpModal}
            />
          ) : (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsLoginModalOpen(true)}
              className="px-3 py-1.5"
              title={t('sidebar.login', 'Iniciar sesión')}
            >
              <LogIn className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">{t('sidebar.login', 'Iniciar sesión')}</span>
            </Button>
          )}
        </div>
      </div>

      {/* Login Modal */}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
      />

      {/* Profile Modal */}
      <ProfileModal
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
      />
    </header>
  );
};

export default TopBar;