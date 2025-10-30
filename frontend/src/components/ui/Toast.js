import React, { useEffect, useState } from 'react';
import { X, Info, AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';

const Toast = ({
  message,
  type = 'info', // 'info', 'success', 'warning', 'error'
  duration = 5000,
  onClose
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    // Trigger entrance animation
    setTimeout(() => setIsVisible(true), 10);

    // Auto-close after duration
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, 300);
  };

  const icons = {
    info: Info,
    success: CheckCircle,
    warning: AlertTriangle,
    error: AlertCircle,
  };

  const styles = {
    info: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800 text-blue-900 dark:text-blue-200',
    success: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800 text-green-900 dark:text-green-200',
    warning: 'bg-amber-50 dark:bg-amber-900/30 border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200',
    error: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800 text-red-900 dark:text-red-200',
  };

  const iconStyles = {
    info: 'text-blue-600 dark:text-blue-400',
    success: 'text-green-600 dark:text-green-400',
    warning: 'text-amber-600 dark:text-amber-400',
    error: 'text-red-600 dark:text-red-400',
  };

  const Icon = icons[type];

  return (
    <div
      className={clsx(
        'w-[400px] max-w-[calc(100vw-2rem)]',
        'transform transition-all duration-300 ease-out',
        isVisible && !isExiting ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
      )}
    >
      <div
        className={clsx(
          'flex items-start gap-3 p-4 rounded-lg border shadow-lg',
          styles[type]
        )}
      >
        <Icon className={clsx('w-5 h-5 flex-shrink-0 mt-0.5', iconStyles[type])} />
        <p className="flex-1 text-sm font-medium leading-relaxed">
          {message}
        </p>
        <button
          onClick={handleClose}
          className={clsx(
            'flex-shrink-0 hover:opacity-70 transition-opacity',
            iconStyles[type]
          )}
          aria-label="Cerrar"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default Toast;
