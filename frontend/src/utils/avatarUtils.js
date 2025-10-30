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

const ICON_MAP = {
  'bear': bearIcon,
  'bee': beeIcon,
  'camel': camelIcon,
  'cat': catIcon,
  'clown-fish': clownFishIcon,
  'cow': cowIcon,
  'crocodile': crocodileIcon,
  'dog': dogIcon,
  'dolphin': dolphinIcon,
  'elephant': elephantIcon,
  'frog': frogIcon,
  'giraffe': giraffeIcon,
  'jellyfish': jellyfishIcon,
  'kangaroo': kangarooIcon,
  'koala': koalaIcon,
  'ladybug': ladybugIcon,
  'lion': lionIcon,
  'monkey': monkeyIcon,
  'octopus': octopusIcon,
  'orangutan': orangutanIcon,
  'otter': otterIcon,
  'owl': owlIcon,
  'panda-bear': pandaBearIcon,
  'peacock': peacockIcon,
  'penguin': penguinIcon,
  'platypus': platypusIcon,
  'praying-mantis': prayingMantisIcon,
  'rabbit': rabbitIcon,
  'raccoon': raccoonIcon,
  'red-panda': redPandaIcon,
  'snake': snakeIcon,
  'tiger': tigerIcon,
  'toucan': toucanIcon,
  'whale': whaleIcon,
  'zebra': zebraIcon,
};

const COLOR_MAP = {
  'blue': 'bg-blue-500',
  'red': 'bg-red-500',
  'green': 'bg-green-500',
  'yellow': 'bg-yellow-500',
  'purple': 'bg-purple-500',
  'pink': 'bg-pink-500',
  'indigo': 'bg-indigo-500',
  'teal': 'bg-teal-500',
  'orange': 'bg-orange-500',
  'cyan': 'bg-cyan-500',
  'emerald': 'bg-emerald-500',
  'violet': 'bg-violet-500',
  'fuchsia': 'bg-fuchsia-500',
  'rose': 'bg-rose-500',
  'sky': 'bg-sky-500',
  'lime': 'bg-lime-500',
};

export const getAvatarIcon = (iconId) => {
  return ICON_MAP[iconId] || catIcon;
};

export const getAvatarColorClass = (colorId) => {
  return COLOR_MAP[colorId] || 'bg-blue-500';
};

export const getDefaultAvatar = () => {
  return {
    icon: 'cat',
    color: 'blue'
  };
};
