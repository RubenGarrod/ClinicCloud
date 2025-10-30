import React from 'react';
import { ExternalLink } from 'lucide-react';
import PubMedLogo from '../assets/PMlogo2.png';

// Configuración de logos de fuentes
const sourceConfig = {
  'pubmed': {
    name: 'PubMed',
    domain: 'pubmed.ncbi.nlm.nih.gov',
    logoSrc: PubMedLogo,
    type: 'image'
  },
  'ncbi': {
    name: 'NCBI',
    domain: 'ncbi.nlm.nih.gov',
    logoSrc: PubMedLogo,
    type: 'image'
  },
  // Preparado para futuras fuentes (usar iconos como placeholder)
  'arxiv': {
    name: 'arXiv',
    domain: 'arxiv.org',
    type: 'icon',
    color: 'text-red-600 dark:text-red-400'
  },
  'nature': {
    name: 'Nature',
    domain: 'nature.com',
    type: 'icon',
    color: 'text-green-700 dark:text-green-400'
  },
  'ieee': {
    name: 'IEEE',
    domain: 'ieee.org',
    type: 'icon',
    color: 'text-blue-800 dark:text-blue-300'
  }
};

// Función para detectar la fuente desde la URL
const detectSource = (url) => {
  if (!url) return null;

  for (const [key, config] of Object.entries(sourceConfig)) {
    if (url.includes(config.domain)) {
      return { key, ...config };
    }
  }

  return null;
};

const SourceLogo = ({ url, showLabel = false, size = 'md' }) => {
  const source = detectSource(url);

  const sizeClasses = {
    sm: 'h-4',
    md: 'h-5',
    lg: 'h-6'
  };

  if (!source) {
    // Fallback al icono genérico de ExternalLink
    const iconSize = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-6 h-6' : 'w-5 h-5';
    return <ExternalLink className={iconSize} />;
  }

  return (
    <div className="flex items-center gap-2">
      {source.type === 'image' ? (
        <img
          src={source.logoSrc}
          alt={source.name}
          className={`${sizeClasses[size]} object-contain`}
          style={{ height: size === 'sm' ? '16px' : size === 'lg' ? '24px' : '20px' }}
        />
      ) : (
        <ExternalLink
          className={`${size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-6 h-6' : 'w-5 h-5'} ${source.color || ''}`}
        />
      )}
      {showLabel && (
        <span className="text-sm font-medium">{source.name}</span>
      )}
    </div>
  );
};

export default SourceLogo;
