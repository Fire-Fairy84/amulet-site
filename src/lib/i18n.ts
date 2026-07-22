export const SITE_URL = 'https://amulet.cards';
export const LANGUAGES = ['en', 'es'] as const;
export type Language = (typeof LANGUAGES)[number];

export const labels = {
  en: {
    cardIndex: 'Tarot card meanings', major: 'Major Arcana', minor: 'Minor Arcana',
    upright: 'Upright', reversed: 'Reversed', work: 'At work', love: 'In love',
    self: 'In you', note: 'Note', previous: 'Previous card', next: 'Next card',
    related: 'Related cards', language: 'Language', english: 'English', spanish: 'Español',
    skip: 'Skip to content', home: 'Home', number: 'Number', allCards: 'All cards',
    journal: 'Keep a journal of your readings',
    cta: 'Draw your daily card in the app or log your own reading. AMULET keeps every reading and shows you what returns over time. No account, no subscription.',
    appStore: 'Download on the App Store', comingSoon: 'Coming soon to the App Store',
    privacy: 'Privacy', terms: 'Terms', contact: 'Contact',
    cups: 'Cups', pentacles: 'Pentacles', swords: 'Swords', wands: 'Wands',
  },
  es: {
    cardIndex: 'Significado de las cartas del tarot', major: 'Arcanos mayores', minor: 'Arcanos menores',
    upright: 'Al derecho', reversed: 'Invertida', work: 'En el trabajo', love: 'En el amor',
    self: 'En ti', note: 'Ojo', previous: 'Carta anterior', next: 'Carta siguiente',
    related: 'Cartas relacionadas', language: 'Idioma', english: 'English', spanish: 'Español',
    skip: 'Saltar al contenido', home: 'Inicio', number: 'Número', allCards: 'Todas las cartas',
    journal: 'Lleva un diario de tus tiradas',
    cta: 'Saca tu carta del día en la app o registra tu propia tirada. AMULET guarda cada lectura y te enseña qué vuelve con el tiempo. Sin cuenta, sin suscripción.',
    appStore: 'Descargar en el App Store', comingSoon: 'Próximamente en el App Store',
    privacy: 'Privacidad', terms: 'Términos', contact: 'Contacto',
    cups: 'Copas', pentacles: 'Oros', swords: 'Espadas', wands: 'Bastos',
  },
} as const;

export function cardIndexPath(language: Language): string {
  return language === 'en' ? '/en/cards/' : '/es/cartas/';
}

export function cardPath(language: Language, slug: string): string {
  return `${cardIndexPath(language)}${slug}/`;
}

export function homePath(language: Language): string {
  return `/${language}/`;
}

export function guideIndexPath(language: Language): string {
  return language === 'en' ? '/en/guides/' : '/es/guias/';
}

export function guidePath(language: Language, slug: string): string {
  return `${guideIndexPath(language)}${slug}/`;
}

export function absolute(path: string): string {
  return new URL(path, SITE_URL).href;
}

export function alternateLanguage(language: Language): Language {
  return language === 'en' ? 'es' : 'en';
}
