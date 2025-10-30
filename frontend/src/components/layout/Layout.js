import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import Footer from '../Footer';
import HelpModal from '../HelpModal';
import SettingsModal from '../SettingsModal';
import AIAssistantModal from '../AIAssistantModal';
import ConsentBanner from '../ConsentBanner';

const Layout = ({ children }) => {
  const { sidebarCollapsed, setSidebarCollapsed } = useTheme();
  const [isHelpModalOpen, setIsHelpModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [isAIAssistantModalOpen, setIsAIAssistantModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-200 dark:bg-gray-900 flex relative">
      {/* Left Sidebar gradient - EXTRA LARGE */}
      <div className={`absolute left-0 top-0 bottom-0 bg-gradient-to-r from-white/80 via-white/60 via-white/40 to-transparent dark:from-gray-950/90 dark:via-gray-900/60 dark:via-gray-800/30 dark:to-transparent pointer-events-none z-0 transition-all duration-300 ${sidebarCollapsed ? 'w-48 lg:w-32' : 'w-128 lg:w-96'}`}></div>

      {/* Left Sidebar top gradient - EXTRA LARGE */}
      <div className={`absolute left-0 top-0 h-48 bg-gradient-to-b from-white/70 via-white/50 via-white/30 to-transparent dark:from-gray-950/80 dark:via-gray-900/50 dark:via-gray-800/20 dark:to-transparent pointer-events-none z-0 transition-all duration-300 ${sidebarCollapsed ? 'w-48 lg:w-32' : 'w-128 lg:w-96'}`}></div>

      {/* Left Sidebar bottom gradient - EXTRA LARGE */}
      <div className={`absolute left-0 bottom-0 h-48 bg-gradient-to-t from-white/70 via-white/50 via-white/30 to-transparent dark:from-gray-950/80 dark:via-gray-900/50 dark:via-gray-800/20 dark:to-transparent pointer-events-none z-0 transition-all duration-300 ${sidebarCollapsed ? 'w-48 lg:w-32' : 'w-128 lg:w-96'}`}></div>

      {/* Right Sidebar gradient - EXTRA LARGE */}
      <div className="absolute right-0 top-0 bottom-0 w-48 lg:w-32 bg-gradient-to-l from-white/80 via-white/60 via-white/40 to-transparent dark:from-gray-950/90 dark:via-gray-900/60 dark:via-gray-800/30 dark:to-transparent pointer-events-none z-0"></div>

      {/* Right Sidebar top gradient - EXTRA LARGE */}
      <div className="absolute right-0 top-0 h-48 w-48 lg:w-32 bg-gradient-to-b from-white/70 via-white/50 via-white/30 to-transparent dark:from-gray-950/80 dark:via-gray-900/50 dark:via-gray-800/20 dark:to-transparent pointer-events-none z-0"></div>

      {/* Right Sidebar bottom gradient - EXTRA LARGE */}
      <div className="absolute right-0 bottom-0 h-48 w-48 lg:w-32 bg-gradient-to-t from-white/70 via-white/50 via-white/30 to-transparent dark:from-gray-950/80 dark:via-gray-900/50 dark:via-gray-800/20 dark:to-transparent pointer-events-none z-0"></div>

      {/* Header gradient - dynamic positioning based on sidebar state - EXTRA LARGE */}
      <div className={`absolute top-0 h-48 bg-gradient-to-b from-white/70 via-white/50 via-white/30 to-transparent dark:from-gray-950/80 dark:via-gray-900/50 dark:via-gray-800/20 dark:to-transparent pointer-events-none z-0 transition-all duration-300 ${sidebarCollapsed ? 'left-48 lg:left-32 right-48 lg:right-32' : 'left-128 lg:left-96 right-48 lg:right-32'}`}></div>

      {/* Footer gradient - dynamic positioning based on sidebar state - EXTRA LARGE */}
      <div className={`absolute bottom-0 h-48 bg-gradient-to-t from-white/70 via-white/50 via-white/30 to-transparent dark:from-gray-950/80 dark:via-gray-900/50 dark:via-gray-800/20 dark:to-transparent pointer-events-none z-0 transition-all duration-300 ${sidebarCollapsed ? 'left-48 lg:left-32 right-48 lg:right-32' : 'left-128 lg:left-96 right-48 lg:right-32'}`}></div>
      
      <div className="relative z-10 flex w-full">
      {/* Left Sidebar */}
      <div className="hidden lg:flex">
        <Sidebar
          onOpenHelp={() => setIsHelpModalOpen(true)}
          onOpenSettings={() => setIsSettingsModalOpen(true)}
          onOpenAIAssistant={() => setIsAIAssistantModalOpen(true)}
        />
      </div>

      {/* Mobile Sidebar Overlay */}
      <div className="lg:hidden">
        {!sidebarCollapsed && (
          <>
            <div
              className="fixed inset-0 z-20 bg-gray-600 bg-opacity-50"
              onClick={() => setSidebarCollapsed(true)}
            />
            <div className="fixed inset-y-0 left-0 z-30 w-64">
              <Sidebar
                onOpenHelp={() => setIsHelpModalOpen(true)}
                onOpenSettings={() => setIsSettingsModalOpen(true)}
                onOpenAIAssistant={() => setIsAIAssistantModalOpen(true)}
              />
            </div>
          </>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <TopBar onOpenHelpModal={() => setIsHelpModalOpen(true)} />

        <main className="flex-1">
          <div className="h-full">
            {children}
          </div>
        </main>

        <Footer />
      </div>

      {/* Right Sidebar (Decorative) */}
      <div className="hidden lg:flex">
        <div className="bg-transparent w-16 flex flex-col h-screen sticky top-0"></div>
      </div>
      </div>

      {/* Help Modal */}
      <HelpModal
        isOpen={isHelpModalOpen}
        onClose={() => setIsHelpModalOpen(false)}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
      />

      {/* AI Assistant Modal */}
      <AIAssistantModal
        isOpen={isAIAssistantModalOpen}
        onClose={() => setIsAIAssistantModalOpen(false)}
      />

      {/* Consent Banner */}
      <ConsentBanner />
    </div>
  );
};

export default Layout;