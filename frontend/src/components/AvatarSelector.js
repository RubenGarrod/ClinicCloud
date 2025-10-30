import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Check } from 'lucide-react';
import clsx from 'clsx';
import Modal from './ui/Modal';
import Button from './ui/Button';

// Importar todos los iconos
import bearIcon from '../assets/animal-icons/bear.png';
import beeIcon from '../assets/animal-icons/bee.png';
import camelIcon from '../assets/animal-icons/camel.png';
import catIcon from '../assets/animal-icons/cat.png';
import clownFishIcon from '../assets/animal-icons/clown-fish.png';
import cowIcon from '../assets/animal-icons/cow.png';
import crocodileIcon from '../assets/animal-icons/crocodile.png';
import dogIcon from '../assets/animal-icons/dog.png';
import dolphinIcon from '../assets/animal-icons/dolphin.png';
import elephantIcon from '../assets/animal-icons/elephant.png';
import frogIcon from '../assets/animal-icons/frog.png';
import giraffeIcon from '../assets/animal-icons/giraffe.png';
import jellyfishIcon from '../assets/animal-icons/jellyfish.png';
import kangarooIcon from '../assets/animal-icons/kangaroo.png';
import koalaIcon from '../assets/animal-icons/koala.png';
import ladybugIcon from '../assets/animal-icons/ladybug.png';
import lionIcon from '../assets/animal-icons/lion.png';
import monkeyIcon from '../assets/animal-icons/monkey.png';
import octopusIcon from '../assets/animal-icons/octopus.png';
import orangutanIcon from '../assets/animal-icons/orangutan.png';
import otterIcon from '../assets/animal-icons/otter.png';
import owlIcon from '../assets/animal-icons/owl.png';
import pandaBearIcon from '../assets/animal-icons/panda-bear.png';
import peacockIcon from '../assets/animal-icons/peacock.png';
import penguinIcon from '../assets/animal-icons/penguin.png';
import platypusIcon from '../assets/animal-icons/platypus.png';
import prayingMantisIcon from '../assets/animal-icons/praying-mantis.png';
import rabbitIcon from '../assets/animal-icons/rabbit.png';
import raccoonIcon from '../assets/animal-icons/raccoon.png';
import redPandaIcon from '../assets/animal-icons/red-panda.png';
import snakeIcon from '../assets/animal-icons/snake.png';
import tigerIcon from '../assets/animal-icons/tiger.png';
import toucanIcon from '../assets/animal-icons/toucan.png';
import whaleIcon from '../assets/animal-icons/whale.png';
import zebraIcon from '../assets/animal-icons/zebra.png';

// Definir iconos disponibles
const ANIMAL_ICONS = [
  { id: 'bear', src: bearIcon, name: 'Oso' },
  { id: 'bee', src: beeIcon, name: 'Abeja' },
  { id: 'camel', src: camelIcon, name: 'Camello' },
  { id: 'cat', src: catIcon, name: 'Gato' },
  { id: 'clown-fish', src: clownFishIcon, name: 'Pez Payaso' },
  { id: 'cow', src: cowIcon, name: 'Vaca' },
  { id: 'crocodile', src: crocodileIcon, name: 'Cocodrilo' },
  { id: 'dog', src: dogIcon, name: 'Perro' },
  { id: 'dolphin', src: dolphinIcon, name: 'Delfín' },
  { id: 'elephant', src: elephantIcon, name: 'Elefante' },
  { id: 'frog', src: frogIcon, name: 'Rana' },
  { id: 'giraffe', src: giraffeIcon, name: 'Jirafa' },
  { id: 'jellyfish', src: jellyfishIcon, name: 'Medusa' },
  { id: 'kangaroo', src: kangarooIcon, name: 'Canguro' },
  { id: 'koala', src: koalaIcon, name: 'Koala' },
  { id: 'ladybug', src: ladybugIcon, name: 'Mariquita' },
  { id: 'lion', src: lionIcon, name: 'León' },
  { id: 'monkey', src: monkeyIcon, name: 'Mono' },
  { id: 'octopus', src: octopusIcon, name: 'Pulpo' },
  { id: 'orangutan', src: orangutanIcon, name: 'Orangután' },
  { id: 'otter', src: otterIcon, name: 'Nutria' },
  { id: 'owl', src: owlIcon, name: 'Búho' },
  { id: 'panda-bear', src: pandaBearIcon, name: 'Oso Panda' },
  { id: 'peacock', src: peacockIcon, name: 'Pavo Real' },
  { id: 'penguin', src: penguinIcon, name: 'Pingüino' },
  { id: 'platypus', src: platypusIcon, name: 'Ornitorrinco' },
  { id: 'praying-mantis', src: prayingMantisIcon, name: 'Mantis' },
  { id: 'rabbit', src: rabbitIcon, name: 'Conejo' },
  { id: 'raccoon', src: raccoonIcon, name: 'Mapache' },
  { id: 'red-panda', src: redPandaIcon, name: 'Panda Rojo' },
  { id: 'snake', src: snakeIcon, name: 'Serpiente' },
  { id: 'tiger', src: tigerIcon, name: 'Tigre' },
  { id: 'toucan', src: toucanIcon, name: 'Tucán' },
  { id: 'whale', src: whaleIcon, name: 'Ballena' },
  { id: 'zebra', src: zebraIcon, name: 'Cebra' },
];

// Paleta de colores para el fondo
const BACKGROUND_COLORS = [
  { id: 'blue', class: 'bg-blue-500', name: 'Azul' },
  { id: 'red', class: 'bg-red-500', name: 'Rojo' },
  { id: 'green', class: 'bg-green-500', name: 'Verde' },
  { id: 'yellow', class: 'bg-yellow-500', name: 'Amarillo' },
  { id: 'purple', class: 'bg-purple-500', name: 'Morado' },
  { id: 'pink', class: 'bg-pink-500', name: 'Rosa' },
  { id: 'indigo', class: 'bg-indigo-500', name: 'Índigo' },
  { id: 'teal', class: 'bg-teal-500', name: 'Turquesa' },
  { id: 'orange', class: 'bg-orange-500', name: 'Naranja' },
  { id: 'cyan', class: 'bg-cyan-500', name: 'Cian' },
  { id: 'emerald', class: 'bg-emerald-500', name: 'Esmeralda' },
  { id: 'violet', class: 'bg-violet-500', name: 'Violeta' },
  { id: 'fuchsia', class: 'bg-fuchsia-500', name: 'Fucsia' },
  { id: 'rose', class: 'bg-rose-500', name: 'Rosa Oscuro' },
  { id: 'sky', class: 'bg-sky-500', name: 'Cielo' },
  { id: 'lime', class: 'bg-lime-500', name: 'Lima' },
];

const AvatarSelector = ({ isOpen, onClose, currentAvatar, onSelect }) => {
  const { t } = useTranslation();
  const [selectedIcon, setSelectedIcon] = useState(currentAvatar?.icon || 'cat');
  const [selectedColor, setSelectedColor] = useState(currentAvatar?.color || 'blue');

  const handleSave = () => {
    onSelect({
      icon: selectedIcon,
      color: selectedColor
    });
    onClose();
  };

  const getIconSrc = (iconId) => {
    const icon = ANIMAL_ICONS.find(i => i.id === iconId);
    return icon ? icon.src : catIcon;
  };

  const getColorClass = (colorId) => {
    const color = BACKGROUND_COLORS.find(c => c.id === colorId);
    return color ? color.class : 'bg-blue-500';
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="lg"
      showCloseButton={true}
    >
      <div className="bg-white dark:bg-gray-800">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
          {t('avatar.selectAvatar', 'Selecciona tu avatar')}
        </h2>

        {/* Vista previa */}
        <div className="flex justify-center mb-8">
          <div className={clsx('w-32 h-32 rounded-full flex items-center justify-center p-4', getColorClass(selectedColor))}>
            <img
              src={getIconSrc(selectedIcon)}
              alt="Avatar preview"
              className="w-full h-full object-contain"
            />
          </div>
        </div>

        {/* Selector de color */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
            {t('avatar.backgroundColor', 'Color de fondo')}
          </h3>
          <div className="grid grid-cols-8 gap-2">
            {BACKGROUND_COLORS.map((color) => (
              <button
                key={color.id}
                onClick={() => setSelectedColor(color.id)}
                className={clsx(
                  'w-10 h-10 rounded-full transition-all',
                  color.class,
                  selectedColor === color.id
                    ? 'ring-4 ring-gray-900 dark:ring-white ring-offset-2'
                    : 'hover:scale-110'
                )}
                title={color.name}
              >
                {selectedColor === color.id && (
                  <Check className="w-6 h-6 text-white mx-auto" />
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Selector de icono */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
            {t('avatar.selectIcon', 'Selecciona un animal')}
          </h3>
          <div className="grid grid-cols-7 gap-2 max-h-64 overflow-y-auto p-2">
            {ANIMAL_ICONS.map((icon) => (
              <button
                key={icon.id}
                onClick={() => setSelectedIcon(icon.id)}
                className={clsx(
                  'w-12 h-12 rounded-lg p-2 transition-all hover:scale-110',
                  selectedIcon === icon.id
                    ? 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'
                )}
                title={icon.name}
              >
                <img
                  src={icon.src}
                  alt={icon.name}
                  className="w-full h-full object-contain"
                />
              </button>
            ))}
          </div>
        </div>

        {/* Botones */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <Button
            variant="secondary"
            onClick={onClose}
          >
            {t('common.cancel', 'Cancelar')}
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
          >
            {t('common.save', 'Guardar')}
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default AvatarSelector;
